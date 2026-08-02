#include <algorithm>
#include <array>
#include <bit>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <random>
#include <string>
#include <tuple>
#include <vector>

using Matrix = std::array<std::uint32_t, 32>;
constexpr int N = 32;

static std::uint32_t apply_row(std::uint32_t row, const Matrix& matrix) {
    std::uint32_t result = 0;
    while (row) {
        const int bit = std::countr_zero(row);
        result ^= matrix[bit];
        row &= row - 1;
    }
    return result;
}

static Matrix multiply(const Matrix& left, const Matrix& right) {
    Matrix result{};
    for (int row = 0; row < N; ++row) result[row] = apply_row(left[row], right);
    return result;
}

static Matrix identity() {
    Matrix result{};
    for (int bit = 0; bit < N; ++bit) result[bit] = std::uint32_t{1} << bit;
    return result;
}

static Matrix transition_matrix() {
    Matrix result{};
    for (int source = 0; source < N; ++source) {
        std::uint32_t value = std::uint32_t{1} << source;
        value ^= value >> 13;
        value ^= value << 17;
        value ^= value >> 5;
        for (int output = 0; output < N; ++output) {
            result[output] |= ((value >> output) & 1U) << source;
        }
    }
    return result;
}

static bool invert_checked(Matrix rows, Matrix& inverse) {
    inverse = identity();
    for (int column = 0; column < N; ++column) {
        int pivot = column;
        while (pivot < N && !(rows[pivot] & (std::uint32_t{1} << column))) ++pivot;
        if (pivot == N) return false;
        std::swap(rows[pivot], rows[column]);
        std::swap(inverse[pivot], inverse[column]);
        for (int row = 0; row < N; ++row) {
            if (row != column && (rows[row] & (std::uint32_t{1} << column))) {
                rows[row] ^= rows[column];
                inverse[row] ^= inverse[column];
            }
        }
    }
    return true;
}

struct State {
    Matrix C{};
    Matrix C_inverse{};
    Matrix T{};
    Matrix B{};
};

static bool from_C(const Matrix& C, State& state) {
    Matrix inverse;
    if (!invert_checked(C, inverse)) return false;
    const Matrix A = transition_matrix();
    state.C = C;
    state.C_inverse = inverse;
    state.T = multiply(inverse, A);
    state.B = multiply(state.T, C);
    return true;
}

static bool load_C(const char* path, State& state) {
    if (!path || !*path) return false;
    std::ifstream stream(path);
    if (!stream) return false;
    std::string line;
    std::string last_record;
    while (std::getline(stream, line)) {
        if (line.find("\"C\"") != std::string::npos) last_record = line;
    }
    const auto marker = last_record.find("\"C\"");
    const auto open = marker == std::string::npos
        ? marker : last_record.find('[', marker);
    if (open == std::string::npos) return false;
    Matrix C{};
    std::size_t cursor = open + 1;
    for (int row = 0; row < N; ++row) {
        const auto quote = last_record.find('"', cursor);
        const auto end = quote == std::string::npos
            ? quote : last_record.find('"', quote + 1);
        if (end == std::string::npos) return false;
        C[row] = static_cast<std::uint32_t>(std::strtoull(
            last_record.substr(quote + 1, end - quote - 1).c_str(), nullptr, 16));
        cursor = end + 1;
    }
    return from_C(C, state);
}

static State origin() {
    State result;
    if (!from_C(identity(), result)) std::abort();
    return result;
}

static bool shallow_C(const Matrix& C) {
    for (auto row : C) {
        if (!row || std::popcount(row) > 2) return false;
    }
    return true;
}

// C' = E*C where row dst is XORed with row src.  Since E^-1=E,
// C'^-1=C^-1*E, which toggles inverse column src wherever column dst is set.
static void shear(State& state, int dst, int src) {
    const Matrix A = transition_matrix();
    const auto dst_bit = std::uint32_t{1} << dst;
    const auto src_bit = std::uint32_t{1} << src;
    state.C[dst] ^= state.C[src];
    for (int row = 0; row < N; ++row) {
        if (state.C_inverse[row] & dst_bit) {
            state.C_inverse[row] ^= src_bit;
            state.T[row] ^= A[src];
        }
    }
    state.B = multiply(state.T, state.C);
}

// C'=P*C for a row transposition.  The inverse is C^-1*P, a column swap.
static void swap_rows(State& state, int first, int second) {
    if (first == second) return;
    const Matrix A = transition_matrix();
    const auto first_bit = std::uint32_t{1} << first;
    const auto second_bit = std::uint32_t{1} << second;
    std::swap(state.C[first], state.C[second]);
    for (int row = 0; row < N; ++row) {
        const bool has_first = state.C_inverse[row] & first_bit;
        const bool has_second = state.C_inverse[row] & second_bit;
        if (has_first != has_second) {
            state.C_inverse[row] ^= first_bit | second_bit;
            state.T[row] ^= A[first] ^ A[second];
        }
    }
    state.B = multiply(state.T, state.C);
}

static State random_tree(std::mt19937_64& random) {
    // A row-weight<=2 matrix is invertible exactly when its 32 row-edges form
    // a spanning tree on the 32 input vertices plus a ground vertex.
    constexpr int V = N + 1;
    std::array<int, N - 1> prufer{};
    std::array<int, V> degree{};
    degree.fill(1);
    for (int& value : prufer) {
        value = int(random() % V);
        ++degree[value];
    }
    std::vector<std::pair<int, int>> edges;
    edges.reserve(N);
    for (int value : prufer) {
        int leaf = 0;
        while (degree[leaf] != 1) ++leaf;
        edges.emplace_back(leaf, value);
        --degree[leaf];
        --degree[value];
    }
    int first = -1;
    int second = -1;
    for (int vertex = 0; vertex < V; ++vertex) {
        if (degree[vertex] == 1) {
            if (first < 0) first = vertex;
            else second = vertex;
        }
    }
    edges.emplace_back(first, second);
    std::shuffle(edges.begin(), edges.end(), random);
    Matrix C{};
    for (int row = 0; row < N; ++row) {
        const auto [left, right] = edges[row];
        if (left) C[row] |= std::uint32_t{1} << (left - 1);
        if (right) C[row] |= std::uint32_t{1} << (right - 1);
    }
    State result;
    if (!from_C(C, result)) std::abort();
    return result;
}

struct Cover {
    int xor_count = 1000;
    int pair_count = 0;
    int final_count = 0;
    std::vector<std::uint32_t> pairs;
};

static bool contains(const std::vector<std::uint32_t>& values, std::uint32_t value) {
    return std::find(values.begin(), values.end(), value) != values.end();
}

static std::vector<std::array<std::uint32_t, 2>> pair_options(std::uint32_t row) {
    std::vector<int> support;
    for (auto remaining = row; remaining; remaining &= remaining - 1) {
        support.push_back(std::countr_zero(remaining));
    }
    std::vector<std::array<std::uint32_t, 2>> result;
    if (support.size() == 3) {
        for (int lone : support) {
            result.push_back({row ^ (std::uint32_t{1} << lone), 0});
        }
    } else if (support.size() == 4) {
        const auto unit = [&](int index) { return std::uint32_t{1} << support[index]; };
        result.push_back({unit(0) | unit(1), unit(2) | unit(3)});
        result.push_back({unit(0) | unit(2), unit(1) | unit(3)});
        result.push_back({unit(0) | unit(3), unit(1) | unit(2)});
    }
    return result;
}

static Cover greedy_cover(const State& state) {
    std::vector<std::uint32_t> targets;
    for (const auto* matrix : {&state.B, &state.C}) {
        for (auto row : *matrix) {
            if (!contains(targets, row)) targets.push_back(row);
        }
    }
    Cover cover;
    std::vector<std::uint32_t> finals;
    for (auto row : targets) {
        const int weight = std::popcount(row);
        if (!weight || weight > 4) return cover;
        if (weight == 2) cover.pairs.push_back(row);
        if (weight >= 3) finals.push_back(row);
    }
    std::sort(cover.pairs.begin(), cover.pairs.end());
    cover.pairs.erase(std::unique(cover.pairs.begin(), cover.pairs.end()), cover.pairs.end());
    const auto covered = [&](std::uint32_t row, const std::vector<std::uint32_t>& pairs) {
        for (auto option : pair_options(row)) {
            if (contains(pairs, option[0]) && (!option[1] || contains(pairs, option[1]))) {
                return true;
            }
        }
        return false;
    };
    while (true) {
        std::vector<std::uint32_t> unmet;
        for (auto row : finals) if (!covered(row, cover.pairs)) unmet.push_back(row);
        if (unmet.empty()) break;
        std::array<std::uint32_t, 2> best{};
        auto best_key = std::tuple(-1.0, -1, -3, std::uint32_t{0}, std::uint32_t{0});
        for (auto row : unmet) {
            for (auto option : pair_options(row)) {
                std::vector<std::uint32_t> trial = cover.pairs;
                int added = 0;
                for (auto pair : option) {
                    if (pair && !contains(trial, pair)) {
                        trial.push_back(pair);
                        ++added;
                    }
                }
                if (!added) continue;
                int gain = 0;
                for (auto target : unmet) gain += covered(target, trial);
                const auto key = std::tuple(double(gain) / added, gain, -added,
                                            ~option[0], ~option[1]);
                if (key > best_key) {
                    best_key = key;
                    best = option;
                }
            }
        }
        if (!best[0]) return cover;
        for (auto pair : best) if (pair && !contains(cover.pairs, pair)) cover.pairs.push_back(pair);
        std::sort(cover.pairs.begin(), cover.pairs.end());
    }
    cover.pair_count = int(cover.pairs.size());
    cover.final_count = int(finals.size());
    cover.xor_count = cover.pair_count + cover.final_count;
    return cover;
}

struct Score {
    int bad = 0;
    int b_heavy = 0;
    int t_heavy = 0;
    int label_capacity_bad = 0;
    int excess = 0;
    int squared_excess = 0;
    int maximum = 0;
    int total_weight = 0;
    int t_weight = 0;
    int c_pairs = 0;
    int greedy_xor = 1000;

    auto key() const {
        return std::tuple(bad, label_capacity_bad, excess, squared_excess,
                          maximum, greedy_xor, total_weight, t_weight, c_pairs);
    }
};

static Score score(const State& state) {
    Score result;
    for (auto row : state.C) result.c_pairs += std::popcount(row) == 2;
    for (int index = 0; index < N; ++index) {
        const int b_weight = std::popcount(state.B[index]);
        const int t_weight = std::popcount(state.T[index]);
        result.maximum = std::max({result.maximum, b_weight, t_weight});
        result.total_weight += b_weight;
        result.t_weight += t_weight;
        const int b_extra = std::max(0, b_weight - 4);
        const int t_extra = std::max(0, t_weight - 4);
        const int capacity_extra = std::max(0, t_weight - b_weight);
        result.b_heavy += b_extra != 0;
        result.t_heavy += t_extra != 0;
        result.label_capacity_bad += capacity_extra != 0;
        result.bad += b_extra != 0 || t_extra != 0 || capacity_extra != 0;
        result.excess += b_extra + t_extra + capacity_extra;
        result.squared_excess += b_extra * b_extra + t_extra * t_extra
                               + capacity_extra * capacity_extra;
    }
    if (!result.bad) result.greedy_xor = greedy_cover(state).xor_count;
    return result;
}

static double energy(const Score& value) {
    if (value.bad) {
        return value.bad * 5000.0 + value.squared_excess * 350.0
             + value.excess * 40.0 + value.maximum * 3.0
             + value.total_weight * 0.1 + value.c_pairs * 0.05;
    }
    return value.greedy_xor * 100.0 + value.total_weight * 0.1
         + value.c_pairs * 0.05;
}

static void verify(const State& state) {
    const Matrix A = transition_matrix();
    if (!shallow_C(state.C)) std::abort();
    if (multiply(state.C, state.C_inverse) != identity()) std::abort();
    if (multiply(state.C, state.T) != A) std::abort();
    if (multiply(state.T, state.C) != state.B) std::abort();
}

static void emit(std::uint64_t step, const State& state, const Score& value,
                 const Cover& cover) {
    verify(state);
    std::printf(
        "{\"step\":%llu,\"score\":{\"bad\":%d,\"excess\":%d,"
        "\"b_heavy\":%d,\"t_heavy\":%d,\"label_capacity_bad\":%d,"
        "\"squared_excess\":%d,\"maximum\":%d,\"total_weight\":%d,"
        "\"t_weight\":%d,\"c_pairs\":%d,\"greedy_xor\":%d},\"C\":[",
        static_cast<unsigned long long>(step), value.bad, value.excess,
        value.b_heavy, value.t_heavy, value.label_capacity_bad,
        value.squared_excess, value.maximum, value.total_weight, value.t_weight,
        value.c_pairs, value.greedy_xor);
    for (int i = 0; i < N; ++i) std::printf("%s\"%08x\"", i ? "," : "", state.C[i]);
    std::printf("],\"T\":[");
    for (int i = 0; i < N; ++i) std::printf("%s\"%08x\"", i ? "," : "", state.T[i]);
    std::printf("],\"B\":[");
    for (int i = 0; i < N; ++i) std::printf("%s\"%08x\"", i ? "," : "", state.B[i]);
    std::printf("],\"pairs\":[");
    for (std::size_t i = 0; i < cover.pairs.size(); ++i) {
        std::printf("%s\"%08x\"", i ? "," : "", cover.pairs[i]);
    }
    std::printf("]}\n");
    std::fflush(stdout);
}

int main(int argc, char** argv) {
    const std::uint64_t seed = argc > 1 ? std::strtoull(argv[1], nullptr, 0) : 0x5a1109ULL;
    const std::uint64_t steps = argc > 2 ? std::strtoull(argv[2], nullptr, 0) : 10000000ULL;
    const std::uint64_t restart = argc > 3 ? std::strtoull(argv[3], nullptr, 0) : 250000ULL;
    std::mt19937_64 random(seed);
    State loaded;
    const bool have_start = argc > 4 && load_C(argv[4], loaded);
    State current = have_start ? loaded : origin();
    Score current_score = score(current);
    State best = current;
    Score best_score = current_score;
    int best_xor = 1000;
    emit(0, current, current_score, greedy_cover(current));

    for (std::uint64_t step = 1; step <= steps; ++step) {
        if (restart && step % restart == 0) {
            current = (random() % 12 == 0) ? random_tree(random) : best;
            current_score = score(current);
        }
        State candidate = current;
        const int first = int(random() % N);
        int second = int(random() % (N - 1));
        second += second >= first;
        const int mutation = int(random() % 20);
        if (mutation < 13) {
            if (std::popcount(candidate.C[first] ^ candidate.C[second]) > 2) continue;
            shear(candidate, first, second);
        } else if (mutation < 17) {
            swap_rows(candidate, first, second);
        } else {
            Matrix changed = candidate.C;
            if (random() & 1) {
                changed[first] = std::uint32_t{1} << (random() % N);
            } else {
                int left = int(random() % N);
                int right = int(random() % (N - 1));
                right += right >= left;
                changed[first] = (std::uint32_t{1} << left) | (std::uint32_t{1} << right);
            }
            if (!from_C(changed, candidate)) continue;
        }
        if (!shallow_C(candidate.C)) continue;
        const Score candidate_score = score(candidate);
        const double old_energy = energy(current_score);
        const double new_energy = energy(candidate_score);
        const double phase = restart ? double(step % restart) / restart : double(step) / steps;
        const double temperature = 12000.0 * std::pow(0.00002, phase) + 0.05;
        const double draw = double(random() >> 11) * (1.0 / 9007199254740992.0);
        if (new_energy <= old_energy || draw < std::exp((old_energy - new_energy) / temperature)) {
            current = candidate;
            current_score = candidate_score;
        }

        bool report = false;
        if (candidate_score.key() < best_score.key()) {
            best = candidate;
            best_score = candidate_score;
            report = true;
        }
        if (!candidate_score.bad && candidate_score.greedy_xor < best_xor) {
            best_xor = candidate_score.greedy_xor;
            report = true;
        }
        if (report) {
            const Cover cover = greedy_cover(candidate);
            emit(step, candidate, candidate_score, cover);
            std::fprintf(
                stderr,
                "best step=%llu bad=%d excess=%d squared=%d max=%d total=%d "
                "t_total=%d b_heavy=%d t_heavy=%d capacity_bad=%d "
                "c_pairs=%d xor=%d\n",
                static_cast<unsigned long long>(step), candidate_score.bad,
                candidate_score.excess, candidate_score.squared_excess,
                candidate_score.maximum, candidate_score.total_weight,
                candidate_score.t_weight, candidate_score.b_heavy,
                candidate_score.t_heavy, candidate_score.label_capacity_bad,
                candidate_score.c_pairs, candidate_score.greedy_xor);
        }
    }

    std::fprintf(
        stderr,
        "summary seed=%llu steps=%llu bad=%d excess=%d squared=%d max=%d "
        "total=%d t_total=%d b_heavy=%d t_heavy=%d capacity_bad=%d "
        "c_pairs=%d xor=%d\n",
        static_cast<unsigned long long>(seed), static_cast<unsigned long long>(steps),
        best_score.bad, best_score.excess, best_score.squared_excess,
        best_score.maximum, best_score.total_weight, best_score.t_weight,
        best_score.b_heavy, best_score.t_heavy, best_score.label_capacity_bad,
        best_score.c_pairs, best_score.greedy_xor);
    return 0;
}
