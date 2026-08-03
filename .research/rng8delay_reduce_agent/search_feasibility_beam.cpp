#define RNG_CALIBRATED_LIBRARY
#include "search_calibrated_global.cpp"

#include <numeric>

namespace {

struct BeamOptions {
    int depth = 10;
    int width = 512;
    std::string seeds_path;
    std::string output_path;
};

struct FastScore {
    int bad_rows = 0;
    int squared_excess = 0;
    int maximum_weight = 0;
    int total_weight = 0;
    int timing_violations = 0;
    int timing_excess = 0;

    bool feasible() const { return bad_rows == 0 && timing_violations == 0; }
};

FastScore fast_score(const State& state) {
    FastScore result;
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
    for (int index = 0; index < kBits; ++index) {
        const int steady_weight = std::popcount(state.B[index]);
        const int target_weight = std::popcount(state.T[index]);
        if (steady_weight >= 3 && target_weight > 2) {
            ++result.timing_violations;
            result.timing_excess += target_weight - 2;
        }
    }
    return result;
}

struct BeamState {
    State state{};
    FastScore score{};
    std::uint64_t hash = 0;
};

auto rank_key(const BeamState& item, int objective) {
    const auto& score = item.score;
    int primary = 0;
    int secondary = 0;
    switch (objective) {
        case 0:
            primary = score.bad_rows + score.timing_violations;
            secondary = std::max(score.bad_rows, score.timing_violations);
            break;
        case 1:
            primary = score.bad_rows;
            secondary = score.timing_violations;
            break;
        case 2:
            primary = score.timing_violations;
            secondary = score.bad_rows;
            break;
        case 3:
            primary = 2 * score.bad_rows + score.timing_violations;
            secondary = score.bad_rows + 2 * score.timing_violations;
            break;
        default:
            primary = score.bad_rows + 2 * score.timing_violations;
            secondary = 2 * score.bad_rows + score.timing_violations;
            break;
    }
    return std::tuple(
        primary,
        secondary,
        score.squared_excess + score.timing_excess,
        score.maximum_weight,
        score.total_weight,
        item.hash
    );
}

std::vector<BeamState> select_frontier(
    std::vector<BeamState> candidates,
    int width
) {
    std::sort(candidates.begin(), candidates.end(), [](const auto& left, const auto& right) {
        return left.hash < right.hash;
    });
    candidates.erase(
        std::unique(candidates.begin(), candidates.end(), [](const auto& left, const auto& right) {
            return left.hash == right.hash;
        }),
        candidates.end()
    );

    const int cell_limit = std::max(8, width / 24);
    std::sort(candidates.begin(), candidates.end(), [](const auto& left, const auto& right) {
        const auto left_key = std::tuple(
            left.score.bad_rows,
            left.score.timing_violations,
            left.score.squared_excess + left.score.timing_excess,
            left.score.maximum_weight,
            left.score.total_weight,
            left.hash
        );
        const auto right_key = std::tuple(
            right.score.bad_rows,
            right.score.timing_violations,
            right.score.squared_excess + right.score.timing_excess,
            right.score.maximum_weight,
            right.score.total_weight,
            right.hash
        );
        return left_key < right_key;
    });
    std::map<std::pair<int, int>, int> cell_counts;
    candidates.erase(
        std::remove_if(candidates.begin(), candidates.end(), [&](const auto& item) {
            auto& count = cell_counts[{item.score.bad_rows, item.score.timing_violations}];
            return count++ >= cell_limit;
        }),
        candidates.end()
    );
    if (static_cast<int>(candidates.size()) <= width) return candidates;

    std::vector<BeamState> result;
    result.reserve(width);
    std::set<std::uint64_t> retained;
    const int objective_count = 5;
    const int quota = std::max(1, width / objective_count);
    std::vector<std::size_t> indexes(candidates.size());
    for (int objective = 0; objective < objective_count; ++objective) {
        std::iota(indexes.begin(), indexes.end(), 0);
        const int take = std::min<int>(quota, indexes.size());
        std::partial_sort(
            indexes.begin(), indexes.begin() + take, indexes.end(),
            [&](std::size_t left, std::size_t right) {
                return rank_key(candidates[left], objective)
                     < rank_key(candidates[right], objective);
            }
        );
        for (int index = 0; index < take && static_cast<int>(result.size()) < width; ++index) {
            const auto& item = candidates[indexes[index]];
            if (retained.insert(item.hash).second) result.push_back(item);
        }
    }
    if (static_cast<int>(result.size()) < width) {
        std::sort(candidates.begin(), candidates.end(), [](const auto& left, const auto& right) {
            return rank_key(left, 0) < rank_key(right, 0);
        });
        for (const auto& item : candidates) {
            if (static_cast<int>(result.size()) >= width) break;
            if (retained.insert(item.hash).second) result.push_back(item);
        }
    }
    return result;
}

void write_states(const std::string& path, const std::vector<BeamState>& states) {
    std::ofstream output(path, std::ios::trunc);
    if (!output) throw std::runtime_error("cannot create beam output JSONL");
    for (const auto& item : states) {
        emit(output, {item.state, evaluate(item.state), item.hash});
    }
}

}  // namespace

int main(int argc, char** argv) {
    BeamOptions options;
    for (int index = 1; index < argc; ++index) {
        const std::string argument = argv[index];
        auto next = [&]() -> std::string {
            if (++index >= argc) throw std::runtime_error("missing argument value");
            return argv[index];
        };
        if (argument == "--depth") options.depth = std::stoi(next());
        else if (argument == "--width") options.width = std::stoi(next());
        else if (argument == "--seeds") options.seeds_path = next();
        else if (argument == "--output") options.output_path = next();
        else throw std::runtime_error("unknown argument: " + argument);
    }
    if (options.seeds_path.empty() || options.output_path.empty()) {
        throw std::runtime_error("--seeds and --output are required");
    }

    std::vector<BeamState> frontier;
    for (const auto& state : read_seeds(options.seeds_path)) {
        frontier.push_back({state, fast_score(state), state_hash(state.T)});
    }
    frontier = select_frontier(std::move(frontier), options.width);

    for (int depth = 0; depth <= options.depth; ++depth) {
        std::vector<BeamState> hits;
        for (const auto& item : frontier) {
            if (item.score.feasible()) hits.push_back(item);
        }
        const auto best = *std::min_element(frontier.begin(), frontier.end(), [](const auto& a, const auto& b) {
            return rank_key(a, 0) < rank_key(b, 0);
        });
        std::fprintf(
            stderr,
            "depth=%d frontier=%zu best_bad=%d best_timing=%d excess=%d maxw=%d hits=%zu\n",
            depth, frontier.size(), best.score.bad_rows, best.score.timing_violations,
            best.score.squared_excess + best.score.timing_excess,
            best.score.maximum_weight, hits.size()
        );
        if (!hits.empty()) {
            write_states(options.output_path, hits);
            return 0;
        }
        if (depth == options.depth) break;

        std::vector<BeamState> candidates;
        candidates.reserve(frontier.size() * kBits * (kBits - 1));
        for (const auto& item : frontier) {
            for (int destination = 0; destination < kBits; ++destination) {
                for (int source = 0; source < kBits; ++source) {
                    if (source == destination) continue;
                    State state = item.state;
                    mutate(state, destination, source);
                    candidates.push_back({state, fast_score(state), state_hash(state.T)});
                }
            }
        }
        frontier = select_frontier(std::move(candidates), options.width);
    }

    write_states(options.output_path, frontier);
    return 1;
}
