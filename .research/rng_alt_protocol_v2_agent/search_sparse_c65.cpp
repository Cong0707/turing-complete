#include <algorithm>
#include <array>
#include <bit>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <random>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>

namespace {

constexpr int N = 32;
constexpr int LIMIT = 16;
using Matrix = std::array<std::uint32_t, N>;
using Caps = std::array<int, N>;

enum class Objective { lexicographic, linear, quadratic };
Objective objective = Objective::lexicographic;

std::uint32_t xs(std::uint32_t value) {
    value ^= value >> 13;
    value ^= value << 17;
    value ^= value >> 5;
    return value;
}

Matrix transition() {
    Matrix result{};
    for (int source = 0; source < N; ++source) {
        const auto value = xs(std::uint32_t{1} << source);
        for (int target = 0; target < N; ++target) {
            result[target] |= ((value >> target) & 1U) << source;
        }
    }
    return result;
}

Matrix identity() {
    Matrix result{};
    for (int bit = 0; bit < N; ++bit) {
        result[bit] = std::uint32_t{1} << bit;
    }
    return result;
}

Matrix xor_matrix(Matrix left, const Matrix& right) {
    for (int row = 0; row < N; ++row) left[row] ^= right[row];
    return left;
}

std::uint32_t apply_row(std::uint32_t row, const Matrix& matrix) {
    std::uint32_t result = 0;
    while (row) {
        const int bit = std::countr_zero(row);
        result ^= matrix[bit];
        row &= row - 1;
    }
    return result;
}

Matrix multiply(const Matrix& left, const Matrix& right) {
    Matrix result{};
    for (int row = 0; row < N; ++row) {
        result[row] = apply_row(left[row], right);
    }
    return result;
}

Matrix inverse(Matrix matrix) {
    Matrix result = identity();
    for (int column = 0; column < N; ++column) {
        int pivot = column;
        while (pivot < N && ((matrix[pivot] >> column) & 1U) == 0) {
            ++pivot;
        }
        if (pivot == N) throw std::runtime_error("singular C");
        std::swap(matrix[column], matrix[pivot]);
        std::swap(result[column], result[pivot]);
        for (int row = 0; row < N; ++row) {
            if (row != column && ((matrix[row] >> column) & 1U)) {
                matrix[row] ^= matrix[column];
                result[row] ^= result[column];
            }
        }
    }
    return result;
}

Caps output_caps(const Matrix& a) {
    Caps result{};
    for (int row = 0; row < N; ++row) {
        result[row] = (LIMIT - std::popcount(a[row])) / 4;
        if (result[row] < 1) {
            throw std::runtime_error("output row has no state-leaf capacity");
        }
    }
    return result;
}

bool row_allowed(std::uint32_t row, int index, const Caps& caps) {
    const int weight = std::popcount(row);
    return weight >= 1 && weight <= caps[index];
}

struct Score {
    int over = 0;
    int excess = 0;
    int maximum = 0;
    int quadratic = 0;
    int combined_weight = 0;
    int b_weight = 0;
    int d_weight = 0;
    int c_weight = 0;

    auto key() const {
        return std::tuple(over, excess, maximum, combined_weight,
                          b_weight, d_weight, c_weight);
    }

    double energy() const {
        if (objective == Objective::linear) {
            return 2.0e4 * excess + 1.0e3 * over
                 + 10.0 * combined_weight + c_weight;
        }
        if (objective == Objective::quadratic) {
            return 2.0e4 * quadratic + 1.0e3 * over
                 + 10.0 * combined_weight + c_weight;
        }
        // A temporary extra violation is sometimes needed to repair a heavy
        // row, while excess and maximum still strongly guide the basin.
        return 1.0e6 * over + 2.0e4 * excess
             + 5.0e3 * std::max(0, maximum - LIMIT)
             + 10.0 * combined_weight + c_weight;
    }
};

struct State {
    Matrix C{};
    Matrix P{};
    Matrix T{};
    Matrix B{};
    Matrix D{};
    Score score{};
};

State make_state(const Matrix& c, const Matrix& a, const Matrix& a_plus_i,
                 const Caps& caps) {
    State state;
    state.C = c;
    for (int row = 0; row < N; ++row) {
        if (!row_allowed(c[row], row, caps)) {
            throw std::runtime_error("C row outside its mixed-Kraft cap");
        }
        state.score.c_weight += std::popcount(c[row]);
    }

    // Persistent-seed, 65-cycle parameterization:
    //   P = C^-1
    //   T = P*A
    //   B = T*C
    //   D = T*(A+I)
    state.P = inverse(c);
    state.T = multiply(state.P, a);
    state.B = multiply(state.T, c);
    state.D = multiply(state.T, a_plus_i);

    for (int row = 0; row < N; ++row) {
        const int b_weight = std::popcount(state.B[row]);
        const int d_weight = std::popcount(state.D[row]);
        const int metric = 4 * b_weight + d_weight;
        const int violation = std::max(0, metric - LIMIT);
        state.score.over += metric > LIMIT;
        state.score.excess += violation;
        state.score.quadratic += violation * violation;
        state.score.maximum = std::max(state.score.maximum, metric);
        state.score.b_weight += b_weight;
        state.score.d_weight += d_weight;
        state.score.combined_weight += b_weight + d_weight;
    }
    return state;
}

void verify_protocol(const State& state, const Matrix& a,
                     const Matrix& a_plus_i, const Caps& caps) {
    if (multiply(state.C, state.P) != identity()) {
        throw std::runtime_error("C*P invariant failed");
    }
    if (state.T != multiply(state.P, a)) {
        throw std::runtime_error("T=P*A invariant failed");
    }
    if (state.B != multiply(state.T, state.C)) {
        throw std::runtime_error("B=T*C invariant failed");
    }
    if (state.D != multiply(state.T, a_plus_i)) {
        throw std::runtime_error("D=T*(A+I) invariant failed");
    }

    Matrix q{};
    Matrix expected = a;
    for (int tick = 0; tick < 65; ++tick) {
        const auto output = xor_matrix(multiply(state.C, q), a);
        if (output != expected) {
            throw std::runtime_error("65-tick output replay failed");
        }
        q = xor_matrix(multiply(state.B, q), state.D);
        expected = multiply(a, expected);
    }

    for (int row = 0; row < N; ++row) {
        if (!row_allowed(state.C[row], row, caps)) {
            throw std::runtime_error("output mixed-Kraft cap failed");
        }
        const int output_metric = 4 * std::popcount(state.C[row])
                                + std::popcount(a[row]);
        if (output_metric > LIMIT) {
            throw std::runtime_error("output row exceeds delay-8 Kraft limit");
        }
    }
}

bool parse_matrix(const std::string& line, const char* name, Matrix& output) {
    const std::string marker = std::string{"\""} + name + "\":[";
    auto cursor = line.find(marker);
    if (cursor == std::string::npos) return false;
    cursor += marker.size();
    for (int row = 0; row < N; ++row) {
        cursor = line.find('"', cursor);
        if (cursor == std::string::npos || cursor + 9 >= line.size()) {
            return false;
        }
        output[row] = static_cast<std::uint32_t>(
            std::stoul(line.substr(cursor + 1, 8), nullptr, 16));
        cursor += 10;
    }
    return true;
}

std::vector<Matrix> load_centers(const std::string& path) {
    std::ifstream input(path);
    if (!input) throw std::runtime_error("cannot open center JSONL");
    std::vector<Matrix> result;
    std::string line;
    while (std::getline(input, line)) {
        Matrix c{};
        if (parse_matrix(line, "C", c)) result.push_back(c);
    }
    if (result.empty()) {
        throw std::runtime_error("center JSONL contains no C matrix");
    }
    return result;
}

void emit(std::ostream& output, std::uint64_t run, std::uint64_t step,
          const State& state, const Matrix& a, const Matrix& a_plus_i,
          const Caps& caps) {
    verify_protocol(state, a, a_plus_i, caps);
    output << "{\"run\":" << run << ",\"step\":" << step
           << ",\"model\":\"persistent-seed-c65\""
           << ",\"score\":{\"over\":" << state.score.over
           << ",\"excess\":" << state.score.excess
           << ",\"max\":" << state.score.maximum
           << ",\"quadratic\":" << state.score.quadratic
           << ",\"combined_weight\":" << state.score.combined_weight
           << ",\"B_weight\":" << state.score.b_weight
           << ",\"D_weight\":" << state.score.d_weight
           << ",\"C_weight\":" << state.score.c_weight << "},";
    const auto matrix = [&](const char* name, const Matrix& value) {
        output << "\"" << name << "\":[";
        for (int row = 0; row < N; ++row) {
            output << (row ? ",\"" : "\"") << std::hex << std::setw(8)
                   << std::setfill('0') << value[row] << "\"";
        }
        output << std::dec << ']';
    };
    matrix("T", state.T); output << ',';
    matrix("B", state.B); output << ',';
    matrix("C", state.C); output << ',';
    matrix("D", state.D);
    output << ",\"delay\":8,\"cycles\":65,\"protocol_verified\":true}\n"
           << std::flush;
}

std::uint32_t random_sparse_row(std::mt19937_64& rng, int cap) {
    const int weight = 1 + static_cast<int>(rng() % cap);
    std::uint32_t result = 0;
    while (std::popcount(result) < weight) {
        result |= std::uint32_t{1} << (rng() % N);
    }
    return result;
}

bool mutate_matrix(Matrix& c, const Caps& caps, std::mt19937_64& rng) {
    const int operation = rng() % 100;
    if (operation < 35) {
        // Right transvection C <- C*E(destination,source).
        int destination = rng() % N;
        int source = rng() % (N - 1);
        if (source >= destination) ++source;
        const auto destination_bit = std::uint32_t{1} << destination;
        const auto source_bit = std::uint32_t{1} << source;
        for (int row = 0; row < N; ++row) {
            if (c[row] & destination_bit) c[row] ^= source_bit;
            if (!row_allowed(c[row], row, caps)) return false;
        }
        return true;
    }
    if (operation < 60) {
        // Left transvection C <- E(destination,source)*C.
        int destination = rng() % N;
        int source = rng() % (N - 1);
        if (source >= destination) ++source;
        c[destination] ^= c[source];
        return row_allowed(c[destination], destination, caps);
    }
    if (operation < 70) {
        int left = rng() % N;
        int right = rng() % (N - 1);
        if (right >= left) ++right;
        return row_allowed(c[right], left, caps)
            && row_allowed(c[left], right, caps)
            && (std::swap(c[left], c[right]), true);
    }
    if (operation < 88) {
        const int row = rng() % N;
        c[row] ^= std::uint32_t{1} << (rng() % N);
        return row_allowed(c[row], row, caps);
    }
    const int row = rng() % N;
    c[row] = random_sparse_row(rng, caps[row]);
    return true;
}

bool propose(const State& current, State& proposal, const Matrix& a,
             const Matrix& a_plus_i, const Caps& caps,
             std::mt19937_64& rng) {
    auto c = current.C;
    const int count_roll = rng() % 1000;
    int moves = count_roll < 820 ? 1 : count_roll < 970 ? 2 : 3;
    while (moves--) {
        if (!mutate_matrix(c, caps, rng)) return false;
    }
    try {
        proposal = make_state(c, a, a_plus_i, caps);
        return true;
    } catch (const std::runtime_error&) {
        return false;
    }
}

State crossover_start(const std::vector<State>& basins, const State& fallback,
                      const Matrix& a, const Matrix& a_plus_i,
                      const Caps& caps, std::mt19937_64& rng) {
    if (basins.size() < 2) return fallback;
    State best = fallback;
    for (int attempt = 0; attempt < 256; ++attempt) {
        const auto& left = basins[static_cast<std::size_t>(rng() % basins.size())];
        const auto& right = basins[static_cast<std::size_t>(rng() % basins.size())];
        if (left.C == right.C) continue;
        auto c = left.C;
        if ((rng() & 3U) == 0) {
            for (int row = 0; row < N; ++row) {
                if (rng() & 1U) c[row] = right.C[row];
            }
        } else {
            const int replacements = 1 + static_cast<int>(rng() % 12);
            std::uint32_t selected = 0;
            while (std::popcount(selected) < replacements) {
                selected |= std::uint32_t{1} << (rng() % N);
            }
            while (selected) {
                const int row = std::countr_zero(selected);
                c[row] = right.C[row];
                selected &= selected - 1;
            }
        }
        try {
            auto candidate = make_state(c, a, a_plus_i, caps);
            if (candidate.score.energy() < best.score.energy()) {
                best = std::move(candidate);
            }
        } catch (const std::runtime_error&) {
        }
    }
    return best;
}

}  // namespace

int main(int argc, char** argv) {
    if (argc < 6) {
        std::cerr << "usage: search_sparse_c65 STEPS RESTARTS SEED CENTERS OUTPUT "
                     "[MORE_CENTERS...] [--linear|--quadratic]\n";
        return 4;
    }
    const auto steps = std::stoull(argv[1]);
    const int restarts = std::stoi(argv[2]);
    const auto seed = std::stoull(argv[3], nullptr, 0);
    const std::string center_path = argv[4];
    const std::string output_path = argv[5];
    const auto a = transition();
    auto a_plus_i = a;
    for (int bit = 0; bit < N; ++bit) {
        a_plus_i[bit] ^= std::uint32_t{1} << bit;
    }
    const auto caps = output_caps(a);
    auto centers = load_centers(center_path);
    for (int index = 6; index < argc; ++index) {
        if (std::string{argv[index]} == "--quadratic") {
            objective = Objective::quadratic;
            continue;
        }
        if (std::string{argv[index]} == "--linear") {
            objective = Objective::linear;
            continue;
        }
        const auto more = load_centers(argv[index]);
        centers.insert(centers.end(), more.begin(), more.end());
    }

    std::vector<State> basin_seeds;
    State global;
    global.score.over = std::numeric_limits<int>::max();
    global.score.excess = std::numeric_limits<int>::max();
    for (const auto& c : centers) {
        try {
            auto state = make_state(c, a, a_plus_i, caps);
            const auto duplicate = std::find_if(
                basin_seeds.begin(), basin_seeds.end(),
                [&](const State& existing) { return existing.C == state.C; });
            if (duplicate == basin_seeds.end()) basin_seeds.push_back(state);
            if (state.score.key() < global.score.key()) global = std::move(state);
        } catch (const std::runtime_error&) {
        }
    }
    if (global.score.over == std::numeric_limits<int>::max()) {
        std::cerr << "no center satisfies the output-row caps\n";
        return 5;
    }

    std::ofstream output(output_path, std::ios::app);
    if (!output) return 3;
    emit(output, 0, 0, global, a, a_plus_i, caps);
    std::cerr << "initial over=" << global.score.over
              << " excess=" << global.score.excess
              << " max=" << global.score.maximum
              << " quadratic=" << global.score.quadratic
              << " weight=" << global.score.combined_weight
              << " basins=" << basin_seeds.size() << "\n";
    if (global.score.over == 0) return 0;

    std::mt19937_64 rng(seed);
    std::uniform_real_distribution<double> unit(0.0, 1.0);
    auto energy_best = *std::min_element(
        basin_seeds.begin(), basin_seeds.end(),
        [](const State& left, const State& right) {
            return left.score.energy() < right.score.energy();
        });
    std::uint64_t proposed = 0;
    std::uint64_t evaluated = 0;
    std::uint64_t accepted = 0;
    constexpr std::uint64_t window = 250'000;
    for (int restart = 0; restart < restarts; ++restart) {
        auto current = restart == 0
            ? global
            : crossover_start(basin_seeds, energy_best, a, a_plus_i, caps, rng);
        for (int move = 0, count = restart == 0 ? 0 : 2 + rng() % 12;
             move < count; ++move) {
            State perturbed;
            if (propose(current, perturbed, a, a_plus_i, caps, rng)) {
                current = std::move(perturbed);
            }
        }
        for (std::uint64_t step = 1; step <= steps; ++step) {
            const auto in_window = (step - 1) % window;
            if (in_window == 0 && step != 1) {
                const auto roll = rng() % 4;
                current = roll == 0 ? global
                        : roll == 1 ? energy_best
                        : roll == 2 ? crossover_start(
                              basin_seeds, energy_best, a, a_plus_i, caps, rng)
                        : basin_seeds[static_cast<std::size_t>(
                              rng() % basin_seeds.size())];
            }
            State candidate;
            ++proposed;
            if (!propose(current, candidate, a, a_plus_i, caps, rng)) continue;
            ++evaluated;
            const double phase = static_cast<double>(in_window) / window;
            const double temperature =
                (objective == Objective::quadratic ? 5.0e6 : 1.0e6)
                * std::pow(1.0 - phase, 3) + 50.0;
            const double delta = candidate.score.energy() - current.score.energy();
            if (delta <= 0 || unit(rng) < std::exp(-delta / temperature)) {
                current = std::move(candidate);
                ++accepted;
            }
            bool should_emit = false;
            if (current.score.key() < global.score.key()) {
                global = current;
                basin_seeds.push_back(current);
                should_emit = true;
                std::cerr << "best run=" << restart << " step=" << step
                          << " over=" << global.score.over
                          << " excess=" << global.score.excess
                          << " max=" << global.score.maximum
                          << " quadratic=" << global.score.quadratic
                          << " weight=" << global.score.combined_weight << "\n";
            }
            if (current.score.energy() < energy_best.score.energy()) {
                energy_best = current;
                if (basin_seeds.empty() || basin_seeds.back().C != current.C) {
                    basin_seeds.push_back(current);
                }
                should_emit = true;
                std::cerr << "energy run=" << restart << " step=" << step
                          << " over=" << energy_best.score.over
                          << " excess=" << energy_best.score.excess
                          << " max=" << energy_best.score.maximum
                          << " quadratic=" << energy_best.score.quadratic
                          << " weight=" << energy_best.score.combined_weight << "\n";
            }
            if (should_emit) {
                emit(output, restart, step, current, a, a_plus_i, caps);
                if (global.score.over == 0) return 0;
            }
        }
    }
    std::cerr << "search proposed=" << proposed
              << " evaluated=" << evaluated
              << " accepted=" << accepted << "\n";
    return 2;
}
