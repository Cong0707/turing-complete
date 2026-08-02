#define main rng_basis_walk_main
#include "../rng_basis_search_v2/walk.cpp"
#undef main

#include <array>
#include <cinttypes>
#include <unordered_set>

namespace {

struct GlobalOperation {
    bool left;
    int distance;
};

struct SearchCounters {
    std::array<std::uint64_t, 8> visited{};
    std::array<std::uint64_t, 8> structurally_feasible{};
    std::array<std::array<std::uint64_t, 65>, 8> greedy_xor{};
    std::array<std::uint64_t, 8> emitted{};
};

void apply_global_shear(State& state, GlobalOperation operation) {
    if (operation.left) {
        // Descending order preserves the simultaneous x ^= x << distance rows.
        for (int destination = kBits - 1; destination >= operation.distance;
             --destination) {
            mutate(state, destination, destination - operation.distance);
        }
    } else {
        // Ascending order preserves the simultaneous x ^= x >> distance rows.
        for (int destination = 0; destination + operation.distance < kBits;
             ++destination) {
            mutate(state, destination, destination + operation.distance);
        }
    }
}

void print_operation_sequence(const std::vector<GlobalOperation>& operations) {
    std::printf("\"global_shears\":[");
    for (std::size_t index = 0; index < operations.size(); ++index) {
        const auto operation = operations[index];
        std::printf("%s\"%c%d\"", index ? "," : "",
                    operation.left ? 'L' : 'R', operation.distance);
    }
    std::printf("]");
}

void print_global_candidate(const State& state, const StructuralScore& structural,
                            const CoverScore& cover, const ModeScore& mode,
                            const std::vector<GlobalOperation>& operations) {
    std::printf("{");
    print_operation_sequence(operations);
    std::printf(",\"structural\":{\"bad\":%d,\"excess\":%d,\"max\":%d,\"weight\":%d},",
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
}

State identity_state() {
    Matrix identity{};
    for (int bit = 0; bit < kBits; ++bit) {
        identity[bit] = std::uint32_t{1} << bit;
    }
    const Matrix A = matrix_from_xorshift();
    return {identity, A, A};
}

void enumerate(const State& state, int depth, int minimum_depth, int maximum_depth,
               int record_xor, std::vector<GlobalOperation>& operations,
               std::unordered_set<std::uint64_t>& emitted_hashes,
               SearchCounters& counters) {
    if (depth >= minimum_depth) {
        ++counters.visited[depth];
        const auto structural = structural_score(state);
        if (structural.feasible()) {
            ++counters.structurally_feasible[depth];
            const auto cover = greedy_cover(state);
            if (cover.greedy_xor >= 0 && cover.greedy_xor <= 64) {
                ++counters.greedy_xor[depth][cover.greedy_xor];
            }
            if (cover.greedy_xor <= record_xor) {
                const auto hash = state_hash(state.T);
                if (emitted_hashes.insert(hash).second) {
                    const auto mode = mode_score(state, cover);
                    print_global_candidate(state, structural, cover, mode, operations);
                    ++counters.emitted[depth];
                }
            }
        }
    }
    if (depth == maximum_depth) {
        return;
    }

    for (int direction = 0; direction < 2; ++direction) {
        for (int distance = 1; distance < kBits; ++distance) {
            const GlobalOperation operation{direction != 0, distance};
            State candidate = state;
            apply_global_shear(candidate, operation);
            operations.push_back(operation);
            enumerate(candidate, depth + 1, minimum_depth, maximum_depth,
                      record_xor, operations, emitted_hashes, counters);
            operations.pop_back();
        }
    }
}

}  // namespace

int main(int argc, char** argv) {
    const int minimum_depth = argc > 1 ? std::atoi(argv[1]) : 0;
    const int maximum_depth = argc > 2 ? std::atoi(argv[2]) : 3;
    const int record_xor = argc > 3 ? std::atoi(argv[3]) : 63;
    if (minimum_depth < 0 || maximum_depth < minimum_depth || maximum_depth > 7 ||
        record_xor < 0 || record_xor > 64) {
        std::fprintf(stderr, "usage: global_shear_enum MIN_DEPTH MAX_DEPTH RECORD_XOR\n");
        return 2;
    }

    const State initial = identity_state();
    std::vector<GlobalOperation> operations;
    std::unordered_set<std::uint64_t> emitted_hashes;
    emitted_hashes.reserve(1U << 16);
    SearchCounters counters;
    enumerate(initial, 0, minimum_depth, maximum_depth, record_xor,
              operations, emitted_hashes, counters);

    for (int depth = minimum_depth; depth <= maximum_depth; ++depth) {
        std::fprintf(stderr,
                     "depth=%d visited=%" PRIu64 " structural=%" PRIu64
                     " emitted=%" PRIu64,
                     depth, counters.visited[depth],
                     counters.structurally_feasible[depth], counters.emitted[depth]);
        for (int xor_count = 0; xor_count <= 64; ++xor_count) {
            if (counters.greedy_xor[depth][xor_count]) {
                std::fprintf(stderr, " x%d=%" PRIu64, xor_count,
                             counters.greedy_xor[depth][xor_count]);
            }
        }
        std::fprintf(stderr, "\n");
    }
    return 0;
}
