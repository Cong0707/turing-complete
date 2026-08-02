#include <algorithm>
#include <array>
#include <bit>
#include <bitset>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <random>
#include <string>
#include <tuple>
#include <unordered_set>
#include <vector>

using Matrix = std::array<std::uint32_t, 32>;

namespace {

constexpr int kBits = 32;

std::uint32_t xorshift32(std::uint32_t value) {
    value ^= value >> 13;
    value ^= value << 17;
    value ^= value >> 5;
    return value;
}

Matrix matrix_from_xorshift() {
    Matrix rows{};
    for (int source = 0; source < kBits; ++source) {
        const auto output = xorshift32(std::uint32_t{1} << source);
        for (int target = 0; target < kBits; ++target) {
            rows[target] |= ((output >> target) & 1U) << source;
        }
    }
    return rows;
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
    for (int row = 0; row < kBits; ++row) {
        result[row] = apply_row(left[row], right);
    }
    return result;
}

Matrix inverse(Matrix matrix) {
    Matrix result{};
    for (int row = 0; row < kBits; ++row) {
        result[row] = std::uint32_t{1} << row;
    }
    for (int column = 0; column < kBits; ++column) {
        int pivot = column;
        while (pivot < kBits && ((matrix[pivot] >> column) & 1U) == 0) {
            ++pivot;
        }
        if (pivot == kBits) {
            std::fprintf(stderr, "singular initial basis\n");
            std::exit(2);
        }
        std::swap(matrix[column], matrix[pivot]);
        std::swap(result[column], result[pivot]);
        for (int row = 0; row < kBits; ++row) {
            if (row != column && ((matrix[row] >> column) & 1U)) {
                matrix[row] ^= matrix[column];
                result[row] ^= result[column];
            }
        }
    }
    return result;
}

Matrix right_shear(int distance) {
    Matrix result{};
    for (int bit = 0; bit < kBits; ++bit) {
        result[bit] = std::uint32_t{1} << bit;
        if (bit + distance < kBits) {
            result[bit] ^= std::uint32_t{1} << (bit + distance);
        }
    }
    return result;
}

struct State {
    Matrix T;
    Matrix B;
    Matrix C;
};

State initial_state() {
    const Matrix A = matrix_from_xorshift();
    const Matrix T = multiply(right_shear(17), right_shear(13));
    const Matrix T_inverse = inverse(T);
    const Matrix C = multiply(A, T_inverse);
    const Matrix B = multiply(T, C);
    return {T, B, C};
}

void mutate(State& state, int destination, int source) {
    const std::uint32_t destination_bit = std::uint32_t{1} << destination;
    const std::uint32_t source_bit = std::uint32_t{1} << source;
    state.T[destination] ^= state.T[source];
    for (auto& row : state.B) {
        if (row & destination_bit) {
            row ^= source_bit;
        }
    }
    state.B[destination] ^= state.B[source];
    for (auto& row : state.C) {
        if (row & destination_bit) {
            row ^= source_bit;
        }
    }
}

struct StructuralScore {
    int bad_rows = 0;
    int squared_excess = 0;
    int maximum_weight = 0;
    int total_weight = 0;

    bool feasible() const { return bad_rows == 0; }
    auto key() const {
        return std::tuple(bad_rows, squared_excess, maximum_weight, total_weight);
    }
};

StructuralScore structural_score(const State& state) {
    StructuralScore result;
    for (const Matrix* matrix : {&state.T, &state.B, &state.C}) {
        for (const auto row : *matrix) {
            const int weight = std::popcount(row);
            const int excess = std::max(0, weight - 4);
            result.bad_rows += weight == 0 || weight > 4;
            result.squared_excess += excess * excess;
            result.maximum_weight = std::max(result.maximum_weight, weight);
            result.total_weight += weight;
        }
    }
    return result;
}

std::uint64_t mix64(std::uint64_t value) {
    value ^= value >> 30;
    value *= 0xbf58476d1ce4e5b9ULL;
    value ^= value >> 27;
    value *= 0x94d049bb133111ebULL;
    return value ^ (value >> 31);
}

std::uint64_t state_hash(const Matrix& matrix) {
    std::uint64_t hash = 0x9e3779b97f4a7c15ULL;
    for (const auto row : matrix) {
        hash = mix64(hash ^ row);
    }
    return hash;
}

std::vector<std::uint32_t> unique_targets(const State& state) {
    std::vector<std::uint32_t> result;
    result.reserve(64);
    for (const Matrix* matrix : {&state.B, &state.C}) {
        for (const auto row : *matrix) {
            if (std::find(result.begin(), result.end(), row) == result.end()) {
                result.push_back(row);
            }
        }
    }
    std::sort(result.begin(), result.end());
    return result;
}

std::vector<std::array<std::uint32_t, 2>> pair_options(std::uint32_t row) {
    std::vector<int> bits;
    for (std::uint32_t remaining = row; remaining; remaining &= remaining - 1) {
        bits.push_back(std::countr_zero(remaining));
    }
    std::vector<std::array<std::uint32_t, 2>> result;
    if (bits.size() == 3) {
        for (const int lone : bits) {
            result.push_back({row ^ (std::uint32_t{1} << lone), 0});
        }
    } else if (bits.size() == 4) {
        const auto unit = [&](int index) { return std::uint32_t{1} << bits[index]; };
        result.push_back({unit(0) | unit(1), unit(2) | unit(3)});
        result.push_back({unit(0) | unit(2), unit(1) | unit(3)});
        result.push_back({unit(0) | unit(3), unit(1) | unit(2)});
    }
    return result;
}

bool contains(const std::vector<std::uint32_t>& values, std::uint32_t value) {
    return std::find(values.begin(), values.end(), value) != values.end();
}

struct CoverScore {
    int lower_bound = 1000;
    int greedy_xor = 1000;
    int required_pairs = 0;
    int finals = 0;
    std::vector<std::uint32_t> selected_pairs;
};

CoverScore greedy_cover(const State& state) {
    const auto targets = unique_targets(state);
    CoverScore result;
    std::vector<std::uint32_t> finals;
    for (const auto row : targets) {
        const int weight = std::popcount(row);
        if (weight == 0 || weight > 4) {
            return result;
        }
        if (weight == 2) {
            result.selected_pairs.push_back(row);
        } else if (weight >= 3) {
            finals.push_back(row);
        }
    }
    result.required_pairs = static_cast<int>(result.selected_pairs.size());
    result.finals = static_cast<int>(finals.size());
    result.lower_bound = result.required_pairs + result.finals;

    auto satisfied = [&](std::uint32_t row,
                         const std::vector<std::uint32_t>& selected) {
        for (const auto option : pair_options(row)) {
            if (contains(selected, option[0]) &&
                (option[1] == 0 || contains(selected, option[1]))) {
                return true;
            }
        }
        return false;
    };

    while (true) {
        std::vector<std::uint32_t> unmet;
        for (const auto row : finals) {
            if (!satisfied(row, result.selected_pairs)) {
                unmet.push_back(row);
            }
        }
        if (unmet.empty()) {
            break;
        }

        std::vector<std::array<std::uint32_t, 2>> actions;
        for (const auto row : unmet) {
            for (auto option : pair_options(row)) {
                if (contains(result.selected_pairs, option[0])) {
                    option[0] = 0;
                }
                if (option[1] != 0 && contains(result.selected_pairs, option[1])) {
                    option[1] = 0;
                }
                if (option[0] == 0 && option[1] != 0) {
                    std::swap(option[0], option[1]);
                }
                if (option[0] > option[1] && option[1] != 0) {
                    std::swap(option[0], option[1]);
                }
                if (option[0] == 0) {
                    continue;
                }
                if (std::find(actions.begin(), actions.end(), option) == actions.end()) {
                    actions.push_back(option);
                }
            }
        }

        auto best = actions.front();
        auto best_key = std::tuple(-1.0, -1, -3, std::uint32_t{0}, std::uint32_t{0});
        for (const auto action : actions) {
            auto candidate = result.selected_pairs;
            candidate.push_back(action[0]);
            if (action[1]) {
                candidate.push_back(action[1]);
            }
            const int gain = static_cast<int>(std::count_if(
                unmet.begin(), unmet.end(), [&](std::uint32_t row) {
                    return satisfied(row, candidate);
                }));
            const int size = action[1] ? 2 : 1;
            // Match the Python ordering, including its preference for smaller masks.
            const auto key = std::tuple(
                static_cast<double>(gain) / size, gain, -size,
                ~action[0], ~action[1]);
            if (key > best_key) {
                best_key = key;
                best = action;
            }
        }
        result.selected_pairs.push_back(best[0]);
        if (best[1]) {
            result.selected_pairs.push_back(best[1]);
        }
        std::sort(result.selected_pairs.begin(), result.selected_pairs.end());
        result.selected_pairs.erase(
            std::unique(result.selected_pairs.begin(), result.selected_pairs.end()),
            result.selected_pairs.end());
    }

    for (auto iterator = result.selected_pairs.rbegin();
         iterator != result.selected_pairs.rend();) {
        const std::uint32_t pair = *iterator;
        const bool required = std::find(targets.begin(), targets.end(), pair) != targets.end();
        if (!required) {
            auto candidate = result.selected_pairs;
            candidate.erase(std::find(candidate.begin(), candidate.end(), pair));
            if (std::all_of(finals.begin(), finals.end(),
                            [&](std::uint32_t row) { return satisfied(row, candidate); })) {
                result.selected_pairs = std::move(candidate);
                iterator = result.selected_pairs.rbegin();
                continue;
            }
        }
        ++iterator;
    }

    result.greedy_xor = static_cast<int>(result.selected_pairs.size() + finals.size());
    return result;
}

struct Edge {
    int neighbor;
    std::uint32_t label;
};

struct Residual {
    std::uint32_t target;
    int state_bit;
};

struct ModeScore {
    int penalty = 0;
    int greedy_or = 1000;
    int component_count = 0;

    bool feasible() const { return penalty == 0; }
};

int pair_index(const std::vector<std::uint32_t>& pairs, std::uint32_t pair) {
    const auto iterator = std::lower_bound(pairs.begin(), pairs.end(), pair);
    if (iterator == pairs.end() || *iterator != pair) {
        return -1;
    }
    return static_cast<int>(iterator - pairs.begin());
}

std::array<std::uint32_t, 2> selected_decomposition(
    std::uint32_t row, const std::vector<std::uint32_t>& pairs) {
    for (const auto option : pair_options(row)) {
        if (pair_index(pairs, option[0]) >= 0 &&
            (option[1] == 0 || pair_index(pairs, option[1]) >= 0)) {
            return option;
        }
    }
    return {0, 0};
}

std::vector<std::uint32_t> light_labels() {
    std::vector<std::uint32_t> result{0};
    result.reserve(529);
    for (int first = 0; first < kBits; ++first) {
        result.push_back(std::uint32_t{1} << first);
    }
    for (int first = 0; first < kBits; ++first) {
        for (int second = first + 1; second < kBits; ++second) {
            result.push_back((std::uint32_t{1} << first) |
                             (std::uint32_t{1} << second));
        }
    }
    return result;
}

void add_mapping(std::bitset<1024>& mappings, int seed_bit, int state_bit) {
    mappings.set(seed_bit * kBits + state_bit);
}

ModeScore mode_score(const State& state, const CoverScore& cover) {
    static const std::vector<std::uint32_t> labels = light_labels();
    const auto& pairs = cover.selected_pairs;
    const int pair_count = static_cast<int>(pairs.size());
    std::vector<std::vector<Edge>> adjacency(pair_count);
    std::vector<std::vector<Residual>> residuals(pair_count);
    std::vector<std::uint32_t> exact(pair_count, 0);
    std::vector<bool> has_exact(pair_count, false);
    std::vector<bool> active(pair_count, false);
    std::bitset<1024> global_mappings;
    ModeScore result;

    for (int output = 0; output < kBits; ++output) {
        const auto steady = state.B[output];
        const auto target = state.T[output];
        const int weight = std::popcount(steady);
        if (weight == 1) {
            if (std::popcount(target) != 1) {
                result.penalty += 4 + std::abs(std::popcount(target) - 1);
            } else {
                add_mapping(global_mappings, std::countr_zero(target),
                            std::countr_zero(steady));
            }
        } else if (weight == 2) {
            const int node = pair_index(pairs, steady);
            if (node < 0) {
                result.penalty += 20;
                continue;
            }
            active[node] = true;
            if (has_exact[node] && exact[node] != target) {
                result.penalty += 4 + std::popcount(exact[node] ^ target);
            } else {
                exact[node] = target;
                has_exact[node] = true;
            }
        } else if (weight == 3) {
            const auto decomposition = selected_decomposition(steady, pairs);
            const int node = pair_index(pairs, decomposition[0]);
            if (node < 0) {
                result.penalty += 20;
                continue;
            }
            const auto direct = steady ^ decomposition[0];
            if (std::popcount(direct) != 1) {
                result.penalty += 20;
                continue;
            }
            active[node] = true;
            residuals[node].push_back({target, std::countr_zero(direct)});
        } else if (weight == 4) {
            const auto decomposition = selected_decomposition(steady, pairs);
            const int left = pair_index(pairs, decomposition[0]);
            const int right = pair_index(pairs, decomposition[1]);
            if (left < 0 || right < 0) {
                result.penalty += 20;
                continue;
            }
            active[left] = active[right] = true;
            adjacency[left].push_back({right, target});
            adjacency[right].push_back({left, target});
        } else {
            result.penalty += 20;
        }
    }

    std::vector<bool> visited(pair_count, false);
    for (int root = 0; root < pair_count; ++root) {
        if (!active[root] || visited[root]) {
            continue;
        }
        ++result.component_count;
        std::vector<int> nodes;
        std::vector<std::uint32_t> offsets(pair_count, 0);
        std::vector<bool> has_offset(pair_count, false);
        std::vector<int> stack{root};
        has_offset[root] = true;
        int consistency_penalty = 0;
        while (!stack.empty()) {
            const int node = stack.back();
            stack.pop_back();
            if (visited[node]) {
                continue;
            }
            visited[node] = true;
            nodes.push_back(node);
            for (const auto edge : adjacency[node]) {
                const auto expected = offsets[node] ^ edge.label;
                if (has_offset[edge.neighbor]) {
                    if (offsets[edge.neighbor] != expected) {
                        consistency_penalty +=
                            4 + std::popcount(offsets[edge.neighbor] ^ expected);
                    }
                } else {
                    has_offset[edge.neighbor] = true;
                    offsets[edge.neighbor] = expected;
                    stack.push_back(edge.neighbor);
                }
            }
        }

        int best_penalty = 1000000;
        std::bitset<1024> best_mappings;
        std::size_t best_union_count = 1025;
        for (const auto root_label : labels) {
            int penalty = consistency_penalty;
            std::vector<std::uint32_t> node_labels(pair_count, 0);
            for (const int node : nodes) {
                const auto label = root_label ^ offsets[node];
                node_labels[node] = label;
                penalty += 3 * std::max(0, std::popcount(label) - 2);
                if (has_exact[node] && label != exact[node]) {
                    penalty += 3 + std::popcount(label ^ exact[node]);
                }
                for (const auto residual : residuals[node]) {
                    penalty += 3 * std::max(
                        0, std::popcount(residual.target ^ label) - 1);
                }
            }
            if (penalty > best_penalty) {
                continue;
            }

            std::bitset<1024> local;
            if (penalty == 0) {
                for (const int node : nodes) {
                    const auto label = node_labels[node];
                    for (const auto residual : residuals[node]) {
                        const auto difference = residual.target ^ label;
                        if (difference) {
                            add_mapping(local, std::countr_zero(difference),
                                        residual.state_bit);
                        }
                    }

                    const int left_state = std::countr_zero(pairs[node]);
                    const int right_state = std::countr_zero(
                        pairs[node] & (pairs[node] - 1));
                    if (std::popcount(label) == 1) {
                        const int seed = std::countr_zero(label);
                        auto left = local;
                        auto right = local;
                        add_mapping(left, seed, left_state);
                        add_mapping(right, seed, right_state);
                        if ((global_mappings | left).count() <=
                            (global_mappings | right).count()) {
                            local = std::move(left);
                        } else {
                            local = std::move(right);
                        }
                    } else if (std::popcount(label) == 2) {
                        const int first_seed = std::countr_zero(label);
                        const int second_seed = std::countr_zero(label & (label - 1));
                        auto straight = local;
                        auto crossed = local;
                        add_mapping(straight, first_seed, left_state);
                        add_mapping(straight, second_seed, right_state);
                        add_mapping(crossed, second_seed, left_state);
                        add_mapping(crossed, first_seed, right_state);
                        if ((global_mappings | straight).count() <=
                            (global_mappings | crossed).count()) {
                            local = std::move(straight);
                        } else {
                            local = std::move(crossed);
                        }
                    }
                }
            }

            const auto union_count = (global_mappings | local).count();
            if (penalty < best_penalty ||
                (penalty == best_penalty && union_count < best_union_count)) {
                best_penalty = penalty;
                best_mappings = std::move(local);
                best_union_count = union_count;
            }
        }
        result.penalty += best_penalty;
        if (best_penalty == 0) {
            global_mappings |= best_mappings;
        }
    }

    if (result.penalty == 0) {
        result.greedy_or = static_cast<int>(global_mappings.count());
    }
    return result;
}

void print_matrix(const char* name, const Matrix& matrix) {
    std::printf("\"%s\":[", name);
    for (int index = 0; index < kBits; ++index) {
        std::printf("%s\"%08x\"", index ? "," : "", matrix[index]);
    }
    std::printf("]");
}

void print_candidate(std::uint64_t step, std::uint64_t hash, const State& state,
                     const StructuralScore& structural, const CoverScore& cover,
                     const ModeScore& mode) {
    std::printf("{\"step\":%llu,\"hash\":\"%016llx\",",
                static_cast<unsigned long long>(step),
                static_cast<unsigned long long>(hash));
    std::printf("\"structural\":{\"bad\":%d,\"excess\":%d,\"max\":%d,\"weight\":%d},",
                structural.bad_rows, structural.squared_excess,
                structural.maximum_weight, structural.total_weight);
    std::printf("\"cover\":{\"lower\":%d,\"greedy_xor\":%d,\"required_pairs\":%d,\"finals\":%d},",
                cover.lower_bound, cover.greedy_xor,
                cover.required_pairs, cover.finals);
    std::printf("\"mode\":{\"penalty\":%d,\"greedy_or\":%d,\"components\":%d},",
                mode.penalty, mode.greedy_or, mode.component_count);
    print_matrix("T", state.T);
    std::printf(",");
    print_matrix("B", state.B);
    std::printf(",");
    print_matrix("C", state.C);
    std::printf("}\n");
    std::fflush(stdout);
}

double energy(const StructuralScore& structural, const CoverScore* cover,
              const ModeScore* mode) {
    double result = structural.bad_rows * 400000.0 +
                    structural.squared_excess * 80000.0 +
                    std::max(0, structural.maximum_weight - 4) * 30000.0 +
                    structural.total_weight;
    if (cover != nullptr) {
        result += cover->greedy_xor * 1500.0 + cover->lower_bound * 100.0;
    }
    if (mode != nullptr) {
        result += mode->penalty * 18000.0;
        if (mode->feasible()) {
            result += mode->greedy_or * 500.0;
        }
    }
    return result;
}

int run_bfs(int radius, int record_xor) {
    const State origin = initial_state();
    const Matrix A = matrix_from_xorshift();
    const auto structural = structural_score(origin);
    const auto cover = greedy_cover(origin);
    const auto mode = mode_score(origin, cover);
    if (!structural.feasible() || cover.greedy_xor != 61 ||
        !mode.feasible() || mode.greedy_or != 47 ||
        multiply(origin.C, origin.T) != A || multiply(origin.T, origin.C) != origin.B) {
        std::fprintf(stderr, "initial matrix self-check failed\n");
        return 2;
    }

    std::unordered_set<std::uint64_t> seen;
    seen.reserve(1U << 20);
    const auto origin_hash = state_hash(origin.T);
    seen.insert(origin_hash);
    std::vector<State> frontier{origin};
    print_candidate(0, origin_hash, origin, structural, cover, mode);
    std::uint64_t emitted = 1;
    std::uint64_t mode_feasible = 1;
    int best_budget = 3 * cover.greedy_xor + mode.greedy_or;

    for (int depth = 1; depth <= radius; ++depth) {
        std::vector<State> next;
        next.reserve(frontier.size() * 8);
        std::uint64_t low_xor = 0;
        for (const auto& parent : frontier) {
            for (int destination = 0; destination < kBits; ++destination) {
                for (int source = 0; source < kBits; ++source) {
                    if (source == destination) {
                        continue;
                    }
                    State candidate = parent;
                    mutate(candidate, destination, source);
                    const auto candidate_structural = structural_score(candidate);
                    if (!candidate_structural.feasible()) {
                        continue;
                    }
                    const auto hash = state_hash(candidate.T);
                    if (!seen.insert(hash).second) {
                        continue;
                    }
                    next.push_back(candidate);
                    const auto candidate_cover = greedy_cover(candidate);
                    if (candidate_cover.greedy_xor > record_xor) {
                        continue;
                    }
                    ++low_xor;
                    const auto candidate_mode = mode_score(candidate, candidate_cover);
                    print_candidate(static_cast<std::uint64_t>(depth), hash, candidate,
                                    candidate_structural, candidate_cover,
                                    candidate_mode);
                    ++emitted;
                    if (candidate_mode.feasible()) {
                        ++mode_feasible;
                        best_budget = std::min(
                            best_budget,
                            3 * candidate_cover.greedy_xor + candidate_mode.greedy_or);
                    }
                }
            }
        }
        std::fprintf(stderr,
                     "bfs depth=%d new=%llu total=%llu low_xor=%llu emitted=%llu mode_feasible=%llu best_budget=%d\n",
                     depth, static_cast<unsigned long long>(next.size()),
                     static_cast<unsigned long long>(seen.size()),
                     static_cast<unsigned long long>(low_xor),
                     static_cast<unsigned long long>(emitted),
                     static_cast<unsigned long long>(mode_feasible), best_budget);
        std::fflush(stderr);
        frontier = std::move(next);
        if (frontier.empty()) {
            break;
        }
    }
    return 0;
}

}  // namespace

int main(int argc, char** argv) {
    if (argc > 1 && std::string(argv[1]) == "bfs") {
        const int radius = argc > 2 ? std::atoi(argv[2]) : 6;
        const int record_xor = argc > 3 ? std::atoi(argv[3]) : 63;
        return run_bfs(radius, record_xor);
    }
    const std::uint64_t seed = argc > 1 ? std::strtoull(argv[1], nullptr, 0) : 0x387ULL;
    const std::uint64_t steps = argc > 2 ? std::strtoull(argv[2], nullptr, 0) : 5000000ULL;
    const int record_xor = argc > 3 ? std::atoi(argv[3]) : 63;
    const std::uint64_t restart_period = argc > 4 ? std::strtoull(argv[4], nullptr, 0) : 250000ULL;

    const State origin = initial_state();
    State current = origin;
    StructuralScore current_structural = structural_score(current);
    CoverScore current_cover = greedy_cover(current);
    ModeScore current_mode = mode_score(current, current_cover);
    const Matrix A = matrix_from_xorshift();
    if (!current_structural.feasible() || current_cover.greedy_xor != 61 ||
        !current_mode.feasible() || current_mode.greedy_or != 47 ||
        multiply(origin.C, origin.T) != A || multiply(origin.T, origin.C) != origin.B) {
        std::fprintf(stderr, "initial matrix self-check failed\n");
        return 2;
    }
    double current_energy = energy(current_structural, &current_cover, &current_mode);

    std::unordered_set<std::uint64_t> emitted;
    emitted.reserve(16384);
    const auto origin_hash = state_hash(origin.T);
    emitted.insert(origin_hash);
    print_candidate(0, origin_hash, origin, current_structural, current_cover,
                    current_mode);

    std::mt19937_64 random(seed);
    std::uint64_t feasible_visits = 1;
    std::uint64_t accepted = 0;
    std::uint64_t emitted_count = 1;
    int best_greedy = current_cover.greedy_xor;

    for (std::uint64_t step = 1; step <= steps; ++step) {
        if (restart_period && step % restart_period == 0) {
            current = origin;
            current_structural = structural_score(current);
            current_cover = greedy_cover(current);
            current_mode = mode_score(current, current_cover);
            current_energy = energy(current_structural, &current_cover, &current_mode);
        }

        const int destination = static_cast<int>(random() % kBits);
        int source = static_cast<int>(random() % (kBits - 1));
        source += source >= destination;
        mutate(current, destination, source);
        const StructuralScore candidate_structural = structural_score(current);
        if (!candidate_structural.feasible()) {
            mutate(current, destination, source);
            continue;
        }
        CoverScore candidate_cover;
        ModeScore candidate_mode;
        candidate_cover = greedy_cover(current);
        candidate_mode = mode_score(current, candidate_cover);
        ++feasible_visits;
        const double candidate_energy = energy(candidate_structural, &candidate_cover,
                                               &candidate_mode);

        if (candidate_cover.greedy_xor <= record_xor) {
            const auto hash = state_hash(current.T);
            if (emitted.insert(hash).second) {
                print_candidate(step, hash, current, candidate_structural,
                                candidate_cover, candidate_mode);
                ++emitted_count;
                best_greedy = std::min(best_greedy, candidate_cover.greedy_xor);
            }
        }

        const double phase = static_cast<double>(step % restart_period) /
                             static_cast<double>(restart_period ? restart_period : steps);
        const double temperature = 80000.0 * std::pow(0.0005, phase) + 20.0;
        const double delta = candidate_energy - current_energy;
        const double draw = static_cast<double>(random() >> 11) *
                            (1.0 / 9007199254740992.0);
        if (delta <= 0.0 || draw < std::exp(-delta / temperature)) {
            current_structural = candidate_structural;
            current_energy = candidate_energy;
            current_cover = candidate_cover;
            current_mode = candidate_mode;
            ++accepted;
        } else {
            mutate(current, destination, source);
        }
    }

    std::fprintf(stderr,
                 "summary seed=%llu steps=%llu accepted=%llu feasible_visits=%llu emitted=%llu best_greedy=%d\n",
                 static_cast<unsigned long long>(seed),
                 static_cast<unsigned long long>(steps),
                 static_cast<unsigned long long>(accepted),
                 static_cast<unsigned long long>(feasible_visits),
                 static_cast<unsigned long long>(emitted_count), best_greedy);
    return 0;
}
