#define main rng_basis_walk_main
#include "../rng_basis_search_v2/walk.cpp"
#undef main

#include <cinttypes>

int main(int argc, char** argv) {
    const int radius = argc > 1 ? std::atoi(argv[1]) : 6;
    const int record_xor = argc > 2 ? std::atoi(argv[2]) : 63;
    const State origin = initial_state();

    std::unordered_set<std::uint64_t> seen;
    seen.reserve(1U << 20);
    seen.insert(state_hash(origin.T));
    std::vector<State> frontier{origin};
    ModeScore unscored;
    unscored.penalty = 999;
    print_candidate(0, state_hash(origin.T), origin, structural_score(origin),
                    greedy_cover(origin), unscored);
    std::uint64_t emitted = 1;

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
                    const auto structural = structural_score(candidate);
                    if (!structural.feasible()) {
                        continue;
                    }
                    const auto hash = state_hash(candidate.T);
                    if (!seen.insert(hash).second) {
                        continue;
                    }
                    next.push_back(candidate);
                    const auto cover = greedy_cover(candidate);
                    if (cover.greedy_xor > record_xor) {
                        continue;
                    }
                    ++low_xor;
                    print_candidate(depth, hash, candidate, structural, cover, unscored);
                    ++emitted;
                }
            }
        }
        std::fprintf(stderr,
                     "depth=%d new=%" PRIu64 " total=%" PRIu64
                     " low_xor=%" PRIu64 " emitted=%" PRIu64 "\n",
                     depth, static_cast<std::uint64_t>(next.size()),
                     static_cast<std::uint64_t>(seen.size()), low_xor, emitted);
        std::fflush(stderr);
        frontier = std::move(next);
    }
    return 0;
}
