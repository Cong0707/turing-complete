#define RNG_CALIBRATED_LIBRARY
#include "search_calibrated_global_67.cpp"

#include <array>
#include <fstream>
#include <map>
#include <unordered_set>

// Multi-objective low-memory walk for the corrected 67-cycle model.  A single
// fitted scalar repeatedly returns to best294.  These fronts deliberately keep
// different compromises alive so a low strict bound is not discarded merely
// because its greedy cover is temporarily expensive (and vice versa).

namespace {

constexpr int kObjectiveCount = 6;

struct MultiOptions {
    std::uint64_t seed = 0x67080326ULL;
    std::uint64_t steps = 250'000;
    int runs = 12;
    int macro_length = 10;
    int front_limit = 384;
    std::string seeds_path;
    std::string output_path;
};

double feasible_objective(const Evaluation& evaluation, int objective) {
    const auto& b = evaluation.bound;
    switch (objective) {
        case 0:
            return evaluation.energy;
        case 1:
            return b.strict_logic + 0.08 * b.proxy_logic
                 + 0.015 * evaluation.structural.total_weight;
        case 2:
            return b.proxy_logic + 0.08 * b.strict_logic
                 + 0.015 * evaluation.structural.total_weight;
        case 3:
            return 0.55 * b.strict_logic + 0.45 * b.proxy_logic
                 + 0.01 * evaluation.structural.total_weight;
        case 4:
            // Both bounds must move before max(strict, proxy-12) improves.
            return std::max<double>(b.strict_logic, b.proxy_logic - 12)
                 + 0.02 * b.greedy_xor;
        case 5:
            // A constructive proxy which exposes pair/mode sharing directly.
            return 3.0 * b.greedy_xor + b.mode_or_lower + b.dual_pair_lower
                 + b.direct_not_lower + 4.0 * b.forced_low_finals;
        default:
            throw std::runtime_error("unknown objective");
    }
}

double search_energy(const Evaluation& evaluation, int objective) {
    if (evaluation.structural.feasible() && evaluation.bound.feasible) {
        return feasible_objective(evaluation, objective);
    }
    // Keep a one-row bridge reachable early in each anneal, but make every
    // fully feasible state preferable once the temperature cools.
    return 340.0
         + 42.0 * evaluation.structural.bad_rows
         + 5.0 * evaluation.structural.squared_excess
         + 2.0 * std::max(0, evaluation.structural.maximum_weight - 4)
         + 18.0 * !evaluation.bound.feasible;
}

using FrontKey = std::tuple<double, int, int, int, int, std::uint64_t>;

struct Front {
    explicit Front(int objective, int limit) : objective(objective), limit(limit) {}

    void insert(const State& state, const Evaluation& evaluation) {
        if (!evaluation.structural.feasible() || !evaluation.bound.feasible) return;
        const auto hash = state_hash(state.T);
        if (!hashes.insert(hash).second) return;
        const auto& b = evaluation.bound;
        const FrontKey key{
            feasible_objective(evaluation, objective),
            b.strict_logic,
            b.proxy_logic,
            b.greedy_xor,
            evaluation.structural.total_weight,
            hash,
        };
        entries.emplace(key, Elite{state, evaluation, hash});
        if (static_cast<int>(entries.size()) > limit) {
            auto last = std::prev(entries.end());
            hashes.erase(last->second.hash);
            entries.erase(last);
        }
    }

    const Elite& sample(std::mt19937_64& random, std::size_t pool) const {
        const auto count = std::min(pool, entries.size());
        auto iterator = entries.begin();
        std::advance(iterator, static_cast<std::ptrdiff_t>(random() % count));
        return iterator->second;
    }

    int objective;
    int limit;
    std::map<FrontKey, Elite> entries;
    std::unordered_set<std::uint64_t> hashes;
};

void apply_word_shear(State& state, std::mt19937_64& random) {
    const int distance = 1 + static_cast<int>(random() % (kBits - 1));
    const bool right = (random() & 1U) != 0;
    const bool reverse = (random() & 1U) != 0;
    if (right) {
        if (!reverse) {
            for (int destination = 0; destination + distance < kBits; ++destination) {
                mutate(state, destination, destination + distance);
            }
        } else {
            for (int destination = kBits - distance - 1; destination >= 0; --destination) {
                mutate(state, destination, destination + distance);
            }
        }
    } else if (!reverse) {
        for (int destination = kBits - 1; destination >= distance; --destination) {
            mutate(state, destination, destination - distance);
        }
    } else {
        for (int destination = distance; destination < kBits; ++destination) {
            mutate(state, destination, destination - distance);
        }
    }
}

void apply_proposal(State& state, std::mt19937_64& random, int macro_length) {
    const auto selector = random() & 63U;
    if (selector < 5) {
        apply_word_shear(state, random);
        if (selector == 0) apply_word_shear(state, random);
    } else {
        apply_macro(state, random, macro_length);
    }
}

}  // namespace

int main(int argc, char** argv) {
    MultiOptions options;
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
        else if (argument == "--front-limit") options.front_limit = std::stoi(next());
        else if (argument == "--seeds") options.seeds_path = next();
        else if (argument == "--output") options.output_path = next();
        else throw std::runtime_error("unknown argument: " + argument);
    }
    if (options.seeds_path.empty() || options.output_path.empty()) {
        throw std::runtime_error("--seeds and --output are required");
    }
    if (options.front_limit < 8 || options.runs < 1) {
        throw std::runtime_error("front limit and runs must be positive");
    }

    std::array<Front, kObjectiveCount> fronts{
        Front(0, options.front_limit), Front(1, options.front_limit),
        Front(2, options.front_limit), Front(3, options.front_limit),
        Front(4, options.front_limit), Front(5, options.front_limit),
    };
    const auto seeds = read_seeds(options.seeds_path);
    for (const auto& state : seeds) {
        const auto evaluation = evaluate(state);
        for (auto& front : fronts) front.insert(state, evaluation);
    }

    std::uint64_t total = 0;
    for (int run = 0; run < options.runs; ++run) {
        const int objective = run % kObjectiveCount;
        std::mt19937_64 random(options.seed
            + static_cast<std::uint64_t>(run) * 0x9e3779b97f4a7c15ULL);
        State current = fronts[objective].sample(random, 96).state;
        for (int kick = 0; kick < run % 5; ++kick) {
            apply_macro(current, random, std::min(4, options.macro_length));
        }
        auto current_evaluation = evaluate(current);
        auto current_energy = search_energy(current_evaluation, objective);

        std::deque<std::uint64_t> tabu_queue;
        std::unordered_set<std::uint64_t> tabu;
        for (std::uint64_t step = 0; step < options.steps; ++step, ++total) {
            State candidate = current;
            apply_proposal(candidate, random, options.macro_length);
            const auto evaluation = evaluate(candidate);
            for (auto& front : fronts) front.insert(candidate, evaluation);

            double candidate_energy = search_energy(evaluation, objective);
            const auto hash = state_hash(candidate.T);
            if (tabu.contains(hash)) candidate_energy += 8.0;
            const double phase = static_cast<double>(step)
                               / std::max(1.0, static_cast<double>(options.steps - 1));
            const double temperature = 82.0 * std::pow(0.0015, phase) + 0.06;
            const double delta = candidate_energy - current_energy;
            const double draw = static_cast<double>(random() >> 11)
                              * (1.0 / 9007199254740992.0);
            if (delta <= 0.0 || draw < std::exp(-delta / temperature)) {
                current = candidate;
                current_evaluation = evaluation;
                current_energy = candidate_energy;
                tabu.insert(hash);
                tabu_queue.push_back(hash);
                if (tabu_queue.size() > 2048) {
                    tabu.erase(tabu_queue.front());
                    tabu_queue.pop_front();
                }
            }
            if (step && step % 100000 == 0) {
                current = fronts[objective].sample(random, 128).state;
                current_evaluation = evaluate(current);
                current_energy = search_energy(current_evaluation, objective);
            }
        }

        std::fprintf(stderr, "run=%d/%d objective=%d total=%llu",
                     run + 1, options.runs, objective,
                     static_cast<unsigned long long>(total));
        for (const auto& front : fronts) {
            const auto& entry = *front.entries.begin();
            const auto& b = entry.second.evaluation.bound;
            std::fprintf(stderr, " o%d=%.3f[%d,%d,x%d]", front.objective,
                         std::get<0>(entry.first), b.strict_logic,
                         b.proxy_logic, b.greedy_xor);
        }
        std::fprintf(stderr, "\n");
    }

    std::map<Matrix, Elite> unique;
    for (const auto& front : fronts) {
        for (const auto& [key, item] : front.entries) {
            (void)key;
            unique.emplace(item.state.T, item);
        }
    }
    std::vector<Elite> output;
    output.reserve(unique.size());
    for (const auto& [matrix, item] : unique) {
        (void)matrix;
        output.push_back(item);
    }
    std::sort(output.begin(), output.end(), [](const Elite& left, const Elite& right) {
        const auto& a = left.evaluation.bound;
        const auto& b = right.evaluation.bound;
        return std::tuple(left.evaluation.energy, a.strict_logic, a.proxy_logic,
                          a.greedy_xor, left.hash)
             < std::tuple(right.evaluation.energy, b.strict_logic, b.proxy_logic,
                          b.greedy_xor, right.hash);
    });
    std::ofstream stream(options.output_path, std::ios::trunc);
    if (!stream) throw std::runtime_error("cannot create output JSONL");
    for (const auto& item : output) emit(stream, item);
    std::fprintf(stderr, "complete seeds=%zu unique=%zu\n", seeds.size(), output.size());
    return 0;
}
