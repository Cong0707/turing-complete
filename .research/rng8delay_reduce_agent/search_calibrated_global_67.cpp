#define main rng_basis_walk_main
#include "../../examples/rng/research/archive/rng_basis_search_v2/walk.cpp"
#undef main

#include <deque>
#include <fstream>
#include <iomanip>
#include <limits>
#include <map>
#include <set>
#include <sstream>

// Low-memory global walk for the 67-cycle, two-phase dual-rail Bit-Switch
// model.  The exact SAT model remains authoritative.  This variant ranks
// distant bases with the fixed regression certificate in
// exact-surrogate-fit.json (2031 exact RC2 records); every retained hit still
// requires a fresh exact solve.
//
// Unlike the earlier 66-cycle search, tick zero is idle and tick one loads
// T*seed.  A heavy B row may therefore carry a weight-three/four load label.
// The only label-width restriction left at this layer is the actual depth-two
// topology: weight-one and weight-three rows have at most three input rails.

namespace {

struct Options {
    std::uint64_t seed = 0xD0A15A17ULL;
    std::uint64_t steps = 2'000'000;
    int runs = 12;
    int macro_length = 8;
    int archive_limit = 512;
    std::string seeds_path;
    std::string output_path;
};

bool parse_matrix(const std::string& line, const char* key, Matrix& matrix) {
    const std::string marker = std::string("\"") + key + "\":[";
    std::size_t cursor = line.find(marker);
    if (cursor == std::string::npos) return false;
    cursor += marker.size();
    for (int index = 0; index < kBits; ++index) {
        cursor = line.find('"', cursor);
        if (cursor == std::string::npos || cursor + 9 >= line.size()) return false;
        char* end = nullptr;
        matrix[index] = static_cast<std::uint32_t>(
            std::strtoul(line.c_str() + cursor + 1, &end, 16));
        if (end != line.c_str() + cursor + 9) return false;
        cursor = static_cast<std::size_t>(end - line.c_str()) + 1;
    }
    return true;
}

std::vector<State> read_seeds(const std::string& path) {
    std::ifstream input(path);
    if (!input) throw std::runtime_error("cannot open seed JSONL: " + path);
    std::vector<State> result;
    std::set<Matrix> seen;
    std::string line;
    const auto A = matrix_from_xorshift();
    while (std::getline(input, line)) {
        State state{};
        if (!parse_matrix(line, "T", state.T)
            || !parse_matrix(line, "B", state.B)
            || !parse_matrix(line, "C", state.C)) {
            throw std::runtime_error("seed matrix parse failure");
        }
        if (multiply(state.C, state.T) != A
            || multiply(state.T, state.C) != state.B) {
            throw std::runtime_error("seed matrix identity failure");
        }
        if (seen.insert(state.T).second) result.push_back(state);
    }

    State identity{};
    identity.B = A;
    identity.C = A;
    for (int index = 0; index < kBits; ++index) {
        identity.T[index] = std::uint32_t{1} << index;
    }
    if (seen.insert(identity.T).second) result.push_back(identity);

    const State baseline = initial_state();
    if (seen.insert(baseline.T).second) result.push_back(baseline);

    if (result.empty()) throw std::runtime_error("no seed matrices loaded");
    return result;
}

std::vector<std::uint32_t> unique_rows(const State& state) {
    std::vector<std::uint32_t> rows;
    rows.reserve(64);
    for (const Matrix* matrix : {&state.B, &state.C}) {
        for (const auto row : *matrix) {
            if (std::find(rows.begin(), rows.end(), row) == rows.end()) {
                rows.push_back(row);
            }
        }
    }
    std::sort(rows.begin(), rows.end());
    return rows;
}

int disjoint_packing_lower(std::vector<std::uint32_t> family) {
    std::sort(family.begin(), family.end(), [](auto left, auto right) {
        return std::tuple(std::popcount(left), left)
             < std::tuple(std::popcount(right), right);
    });
    std::uint32_t occupied = 0;
    int packed = 0;
    for (const auto support : family) {
        if (support != 0 && (support & occupied) == 0) {
            occupied |= support;
            ++packed;
        }
    }
    return packed;
}

struct Bound {
    bool feasible = true;
    int timing_violations = 0;
    int timing_excess = 0;
    int heavy_finals = 0;
    int forced_low_finals = 0;
    int required_pairs = 0;
    int pair_demand = 0;
    int dual_pair_lower = 0;
    int pair_node_lower = 0;
    int mode_or_lower = 32;
    int direct_not_lower = 0;
    int strict_logic = 1000;
    int greedy_xor = 1000;
    int proxy_logic = 1000;
};

void add_pair_capacity(
    std::array<int, 496>& capacities,
    std::uint32_t pair,
    std::set<std::uint32_t>& local
) {
    if (std::popcount(pair) != 2 || !local.insert(pair).second) return;
    int ordinal = 0;
    const int left = std::countr_zero(pair);
    const int right = std::countr_zero(pair & (pair - 1));
    for (int first = 0; first < left; ++first) ordinal += kBits - first - 1;
    ordinal += right - left - 1;
    ++capacities[ordinal];
}

Bound lower_bound(const State& state) {
    Bound result;
    const auto rows = unique_rows(state);
    std::array<int, 496> capacities{};
    std::vector<std::uint32_t> direct_families;

    auto add_final_family = [&](const std::vector<std::uint32_t>& pairs, int demand) {
        std::set<std::uint32_t> local;
        for (const auto pair : pairs) add_pair_capacity(capacities, pair, local);
        result.pair_demand += demand;
    };

    for (const auto row : rows) {
        const int weight = std::popcount(row);
        if (weight == 2) {
            ++result.required_pairs;
        } else if (weight == 3 || weight == 4) {
            ++result.heavy_finals;
            std::vector<std::uint32_t> pairs;
            for (std::uint32_t remaining = row; remaining; remaining &= remaining - 1) {
                const auto left = remaining & (0U - remaining);
                for (std::uint32_t tail = remaining & ~left; tail; tail &= tail - 1) {
                    pairs.push_back(left | (tail & (0U - tail)));
                }
            }
            add_final_family(pairs, weight == 3 ? 1 : 2);
            if (weight == 3) direct_families.push_back(row);
        }
    }

    for (int index = 0; index < kBits; ++index) {
        const auto row = state.B[index];
        const int weight = std::popcount(row);
        const int target_weight = std::popcount(state.T[index]);
        if ((weight == 1 || weight == 3) && target_weight > 3) {
            result.feasible = false;
        }
        if (weight == 1 && target_weight != 1) {
            ++result.forced_low_finals;
            std::vector<std::uint32_t> pairs;
            const int state_bit = std::countr_zero(row);
            for (int other = 0; other < kBits; ++other) {
                if (other != state_bit) pairs.push_back(row | (1U << other));
            }
            add_final_family(pairs, 1);
            direct_families.push_back(~row);
        } else if (weight == 2 && target_weight > 2) {
            ++result.forced_low_finals;
            --result.required_pairs;
            std::vector<std::uint32_t> pairs;
            const int left = std::countr_zero(row);
            const int right = std::countr_zero(row & (row - 1));
            for (int common = 0; common < kBits; ++common) {
                if (common == left || common == right) continue;
                pairs.push_back((1U << left) | (1U << common));
                pairs.push_back((1U << right) | (1U << common));
            }
            add_final_family(pairs, 2);
        }
    }

    std::vector<int> capacity_values;
    for (const int capacity : capacities) {
        if (capacity) capacity_values.push_back(capacity);
    }
    std::sort(capacity_values.rbegin(), capacity_values.rend());
    int supplied = 0;
    while (result.dual_pair_lower < static_cast<int>(capacity_values.size())
           && supplied < result.pair_demand) {
        supplied += capacity_values[result.dual_pair_lower++];
    }
    if (supplied < result.pair_demand) {
        result.feasible = false;
        return result;
    }
    result.pair_node_lower = std::max(result.required_pairs, result.dual_pair_lower);

    int heavy_mode_pack = 0;
    for (int seed = 0; seed < kBits; ++seed) {
        std::vector<std::uint32_t> family;
        for (int output = 0; output < kBits; ++output) {
            if (((state.T[output] >> seed) & 1U)
                && std::popcount(state.B[output]) >= 3) {
                family.push_back(state.B[output]);
            }
        }
        heavy_mode_pack += disjoint_packing_lower(std::move(family));
    }
    result.mode_or_lower = std::max(32, heavy_mode_pack);
    result.direct_not_lower = disjoint_packing_lower(std::move(direct_families));

    const int final_count = result.heavy_finals + result.forced_low_finals;
    result.strict_logic = 4 * final_count
                        + 3 * result.pair_node_lower
                        + result.dual_pair_lower
                        + result.mode_or_lower
                        + result.direct_not_lower;
    const auto cover = greedy_cover(state);
    result.greedy_xor = cover.greedy_xor;
    if (cover.greedy_xor < 1000) {
        const int ordinary_proxy = cover.greedy_xor + 2 * result.forced_low_finals;
        result.proxy_logic = 3 * ordinary_proxy
                           + final_count
                           + result.dual_pair_lower
                           + result.mode_or_lower
                           + result.direct_not_lower;
    }
    return result;
}

struct Evaluation {
    StructuralScore structural{};
    Bound bound{};
    double shape_penalty = 1.0e30;
    double energy = 1.0e30;
};

Evaluation evaluate(const State& state) {
    Evaluation result;
    result.structural = structural_score(state);
    result.bound = lower_bound(state);
    if (!result.structural.feasible() || !result.bound.feasible) {
        result.energy = 300.0
                      + 70.0 * result.structural.bad_rows
                      + 8.0 * result.structural.squared_excess
                      + 16.0 * result.bound.timing_violations
                      + 3.0 * result.bound.timing_excess
                      + 0.01 * result.structural.total_weight;
        if (!result.bound.feasible && !result.bound.timing_violations) {
            result.energy += 40.0;
        }
        result.shape_penalty = result.energy;
        return result;
    }
    const double strict = result.bound.strict_logic;
    const double proxy = result.bound.proxy_logic;
    const double heavy = result.bound.heavy_finals;
    const double forced = result.bound.forced_low_finals;
    const double pair = result.bound.pair_node_lower;
    const double dual = result.bound.dual_pair_lower;
    const double mode = result.bound.mode_or_lower;
    const double direct_not = result.bound.direct_not_lower;
    const double greedy = result.bound.greedy_xor;
    result.energy =
        -38.37381425013302
        + 0.2907130540493803 * strict
        + 1.446975548831352 * proxy
        - 0.7974479435392698 * heavy
        + 1.013165381312974 * forced
        + 0.06141426318165477 * pair
        + 0.06141426302057562 * dual
        + 1.1350581911141866 * mode
        - 1.9528818859109456 * direct_not
        - 1.3637959212621382 * greedy
        - 0.4869901758929597 * heavy * forced
        + 0.21049739406004694 * forced * pair
        + 0.02472894185977398 * heavy * mode
        - 0.11926640371493188 * pair * mode
        + 0.05905225954766324 * (greedy - 61.0) * (greedy - 61.0);
    result.shape_penalty = result.energy;
    return result;
}

struct Elite {
    State state{};
    Evaluation evaluation{};
    std::uint64_t hash = 0;
    auto key() const {
        return std::tuple(
            evaluation.energy,
            !evaluation.structural.feasible(),
            !evaluation.bound.feasible,
            evaluation.bound.proxy_logic,
            evaluation.bound.strict_logic,
            evaluation.bound.forced_low_finals,
            evaluation.structural.total_weight,
            hash
        );
    }
};

void apply_macro(State& state, std::mt19937_64& rng, int maximum_length) {
    int length = 1;
    const auto selector = rng() % 100;
    if (selector >= 55 && selector < 80) length = 2;
    else if (selector >= 80 && selector < 92) length = 3;
    else if (selector >= 92 && selector < 97) length = 4;
    else if (selector >= 97) length = 5 + static_cast<int>(rng() % 4);
    length = std::min(length, maximum_length);
    if ((rng() & 15U) == 0 && length >= 2) {
        const int destination = static_cast<int>(rng() % kBits);
        for (int index = 0; index < length; ++index) {
            int source = static_cast<int>(rng() % (kBits - 1));
            source += source >= destination;
            mutate(state, destination, source);
        }
        return;
    }
    for (int index = 0; index < length; ++index) {
        const int destination = static_cast<int>(rng() % kBits);
        int source = static_cast<int>(rng() % (kBits - 1));
        source += source >= destination;
        mutate(state, destination, source);
    }
}

void emit_matrix(std::ostream& output, const char* name, const Matrix& rows) {
    output << "\"" << name << "\":[";
    for (int index = 0; index < kBits; ++index) {
        output << (index ? ",\"" : "\"") << std::hex << std::setw(8)
               << std::setfill('0') << rows[index] << "\"";
    }
    output << std::dec << ']';
}

void emit(std::ostream& output, const Elite& item) {
    const auto& b = item.evaluation.bound;
    output << "{\"hash\":\"" << std::hex << std::setw(16) << std::setfill('0')
           << item.hash << std::dec << "\",\"surrogate\":"
           << std::fixed << std::setprecision(6) << item.evaluation.energy
           << std::defaultfloat << ",\"structural\":{"
           << "\"bad_rows\":" << item.evaluation.structural.bad_rows
           << ",\"squared_excess\":" << item.evaluation.structural.squared_excess
           << ",\"maximum_weight\":" << item.evaluation.structural.maximum_weight
           << ",\"total_weight\":" << item.evaluation.structural.total_weight
           << "},\"lower\":{"
           << "\"strict_logic\":" << b.strict_logic
           << ",\"proxy_logic\":" << b.proxy_logic
           << ",\"timing_violations\":" << b.timing_violations
           << ",\"timing_excess\":" << b.timing_excess
           << ",\"heavy_finals\":" << b.heavy_finals
           << ",\"forced_low_finals\":" << b.forced_low_finals
           << ",\"pair_node_lower\":" << b.pair_node_lower
           << ",\"dual_pair_lower\":" << b.dual_pair_lower
           << ",\"mode_or_lower\":" << b.mode_or_lower
           << ",\"direct_not_lower\":" << b.direct_not_lower
           << ",\"greedy_xor\":" << b.greedy_xor << "},";
    emit_matrix(output, "T", item.state.T);
    output << ',';
    emit_matrix(output, "B", item.state.B);
    output << ',';
    emit_matrix(output, "C", item.state.C);
    output << "}\n";
}

}  // namespace

#ifndef RNG_CALIBRATED_LIBRARY
int main(int argc, char** argv) {
    Options options;
    for (int index = 1; index < argc; ++index) {
        const std::string argument = argv[index];
        auto next = [&]() -> std::string {
            if (++index >= argc) throw std::runtime_error("missing argument value");
            return argv[index];
        };
        if (argument == "--seed") options.seed = std::stoull(next(), nullptr, 0);
        else if (argument == "--steps") options.steps = std::stoull(next(), nullptr, 0);
        else if (argument == "--runs") options.runs = std::stoi(next());
        else if (argument == "--macro-length") options.macro_length = std::stoi(next());
        else if (argument == "--archive-limit") options.archive_limit = std::stoi(next());
        else if (argument == "--seeds") options.seeds_path = next();
        else if (argument == "--output") options.output_path = next();
        else throw std::runtime_error("unknown argument: " + argument);
    }
    if (options.seeds_path.empty() || options.output_path.empty()) {
        throw std::runtime_error("--seeds and --output are required");
    }
    const auto seeds = read_seeds(options.seeds_path);
    std::vector<Elite> archive;
    std::set<Matrix> archive_matrices;
    auto retain = [&](const State& state, const Evaluation& evaluation) {
        const auto hash = state_hash(state.T);
        if (!archive_matrices.insert(state.T).second) return;
        archive.push_back({state, evaluation, hash});
        std::sort(archive.begin(), archive.end(), [](const Elite& left, const Elite& right) {
            return left.key() < right.key();
        });
        if (static_cast<int>(archive.size()) > options.archive_limit) {
            archive_matrices.erase(archive.back().state.T);
            archive.pop_back();
        }
    };
    for (const auto& state : seeds) retain(state, evaluate(state));

    std::uint64_t total_steps = 0;
    for (int run = 0; run < options.runs; ++run) {
        std::mt19937_64 rng(options.seed
                          + static_cast<std::uint64_t>(run) * 0x9e3779b97f4a7c15ULL);
        State current = seeds[static_cast<std::size_t>(rng() % seeds.size())];
        if (!archive.empty() && run % 3) {
            const auto pool = std::min<std::size_t>(archive.size(), 64);
            current = archive[static_cast<std::size_t>(rng() % pool)].state;
        }
        for (int kick = 0; kick < 1 + run % 7; ++kick) {
            apply_macro(current, rng, std::min(options.macro_length, 4));
        }
        auto current_evaluation = evaluate(current);
        std::deque<std::uint64_t> tabu_queue;
        std::set<std::uint64_t> tabu;
        for (std::uint64_t step = 0; step < options.steps; ++step, ++total_steps) {
            State candidate = current;
            Evaluation candidate_evaluation;
            if ((rng() & 127U) == 0) {
                candidate_evaluation.energy = std::numeric_limits<double>::infinity();
                for (int sample = 0; sample < 8; ++sample) {
                    State trial = current;
                    const int destination = static_cast<int>(rng() % kBits);
                    int source = static_cast<int>(rng() % (kBits - 1));
                    source += source >= destination;
                    mutate(trial, destination, source);
                    auto trial_evaluation = evaluate(trial);
                    if (trial_evaluation.energy < candidate_evaluation.energy) {
                        candidate = std::move(trial);
                        candidate_evaluation = std::move(trial_evaluation);
                    }
                }
            } else {
                apply_macro(candidate, rng, options.macro_length);
                candidate_evaluation = evaluate(candidate);
            }
            const auto hash = state_hash(candidate.T);
            const double phase = static_cast<double>(step)
                               / std::max(1.0, static_cast<double>(options.steps - 1));
            const double temperature = 75.0 * std::pow(0.002, phase) + 0.08;
            double delta = candidate_evaluation.energy - current_evaluation.energy;
            if (tabu.contains(hash)) delta += 12.0;
            const double draw = static_cast<double>(rng() >> 11)
                              * (1.0 / 9007199254740992.0);
            if (delta <= 0.0 || draw < std::exp(-delta / temperature)) {
                current = candidate;
                current_evaluation = candidate_evaluation;
                tabu.insert(hash);
                tabu_queue.push_back(hash);
                if (tabu_queue.size() > 2048) {
                    tabu.erase(tabu_queue.front());
                    tabu_queue.pop_front();
                }
                retain(current, current_evaluation);
            }
            if (step && step % 200000 == 0 && !archive.empty()) {
                const auto pool = std::min<std::size_t>(archive.size(), 96);
                current = archive[static_cast<std::size_t>(rng() % pool)].state;
                current_evaluation = evaluate(current);
            }
        }
        const auto& best = archive.front().evaluation.bound;
        std::fprintf(stderr,
            "run=%d/%d total=%llu archive=%zu best_fit=%.3f best_proxy=%d best_strict=%d\n",
            run + 1, options.runs,
            static_cast<unsigned long long>(total_steps), archive.size(),
            archive.front().evaluation.energy,
            best.proxy_logic, best.strict_logic);
    }

    std::ofstream output(options.output_path, std::ios::trunc);
    if (!output) throw std::runtime_error("cannot create output JSONL");
    for (const auto& item : archive) emit(output, item);
    const auto& best = archive.front().evaluation.bound;
    std::fprintf(stderr,
        "complete seeds=%zu archive=%zu best_fit=%.3f best_proxy=%d best_strict=%d\n",
        seeds.size(), archive.size(), archive.front().evaluation.energy,
        best.proxy_logic, best.strict_logic);
    return 0;
}
#endif
