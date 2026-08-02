#define main rng_basis_walk_main
#include "../rng_basis_search_v2/walk.cpp"
#undef main

#include <array>
#include <cinttypes>
#include <unordered_set>

namespace {

struct Counters {
    std::array<std::uint64_t, 8> visited{};
    std::array<std::uint64_t, 8> structural{};
    std::array<std::uint64_t, 8> emitted{};
};

void print_macro_candidate(const State& state, const StructuralScore& structural,
                           const CoverScore& cover, const ModeScore& mode,
                           int destination, const std::vector<int>& sources) {
    std::printf("{\"macro_destination\":%d,\"macro_sources\":[", destination);
    for (std::size_t index = 0; index < sources.size(); ++index) {
        std::printf("%s%d", index ? "," : "", sources[index]);
    }
    std::printf("],\"cover\":{\"lower\":%d,\"greedy_xor\":%d,\"required_pairs\":%d,\"finals\":%d},",
                cover.lower_bound, cover.greedy_xor,
                cover.required_pairs, cover.finals);
    std::printf("\"mode\":{\"penalty\":%d,\"greedy_or\":%d,\"components\":%d},",
                mode.penalty, mode.greedy_or, mode.component_count);
    std::printf("\"structural\":{\"bad\":%d,\"excess\":%d,\"max\":%d,\"weight\":%d},",
                structural.bad_rows, structural.squared_excess,
                structural.maximum_weight, structural.total_weight);
    print_matrix("T", state.T);
    std::printf(",");
    print_matrix("B", state.B);
    std::printf(",");
    print_matrix("C", state.C);
    std::printf("}\n");
}

void choose_sources(const State& origin, int destination, int next_source,
                    int remaining, int record_xor, std::vector<int>& sources,
                    std::unordered_set<std::uint64_t>& emitted_hashes,
                    Counters& counters) {
    if (remaining == 0) {
        const int arity = static_cast<int>(sources.size());
        ++counters.visited[arity];
        State candidate = origin;
        for (const int source : sources) {
            mutate(candidate, destination, source);
        }
        const auto structural = structural_score(candidate);
        if (!structural.feasible()) {
            return;
        }
        ++counters.structural[arity];
        const auto cover = greedy_cover(candidate);
        if (cover.greedy_xor > record_xor) {
            return;
        }
        const auto hash = state_hash(candidate.T);
        if (!emitted_hashes.insert(hash).second) {
            return;
        }
        const auto mode = mode_score(candidate, cover);
        print_macro_candidate(candidate, structural, cover, mode,
                              destination, sources);
        ++counters.emitted[arity];
        return;
    }

    for (int source = next_source; source < kBits; ++source) {
        if (source == destination || kBits - source < remaining) {
            continue;
        }
        sources.push_back(source);
        choose_sources(origin, destination, source + 1, remaining - 1,
                       record_xor, sources, emitted_hashes, counters);
        sources.pop_back();
    }
}

}  // namespace

int main(int argc, char** argv) {
    const int minimum_arity = argc > 1 ? std::atoi(argv[1]) : 2;
    const int maximum_arity = argc > 2 ? std::atoi(argv[2]) : 5;
    const int record_xor = argc > 3 ? std::atoi(argv[3]) : 63;
    if (minimum_arity < 1 || maximum_arity < minimum_arity || maximum_arity > 7) {
        std::fprintf(stderr, "usage: macro_row_enum MIN_ARITY MAX_ARITY RECORD_XOR\n");
        return 2;
    }

    const State origin = initial_state();
    std::unordered_set<std::uint64_t> emitted_hashes;
    emitted_hashes.reserve(1U << 16);
    std::vector<int> sources;
    Counters counters;
    for (int arity = minimum_arity; arity <= maximum_arity; ++arity) {
        for (int destination = 0; destination < kBits; ++destination) {
            choose_sources(origin, destination, 0, arity, record_xor,
                           sources, emitted_hashes, counters);
        }
        std::fprintf(stderr,
                     "arity=%d visited=%" PRIu64 " structural=%" PRIu64
                     " emitted=%" PRIu64 "\n",
                     arity, counters.visited[arity], counters.structural[arity],
                     counters.emitted[arity]);
        std::fflush(stderr);
    }
    return 0;
}
