#define main rng_basis_walk_main
#include "../rng_basis_search_v2/walk.cpp"
#undef main

#include <array>
#include <atomic>
#include <cinttypes>
#include <cstddef>
#include <mutex>
#include <omp.h>
#include <unordered_set>
#include <utility>

namespace {

constexpr std::size_t kSeenShards = 64;
constexpr std::size_t kBatchSize = 64;

struct SeenShard {
    std::mutex mutex;
    std::unordered_set<std::uint64_t> hashes;
};

std::uint64_t seen_size(const std::array<SeenShard, kSeenShards>& shards) {
    std::uint64_t total = 0;
    for (const auto& shard : shards) {
        total += shard.hashes.size();
    }
    return total;
}

bool mark_seen(std::array<SeenShard, kSeenShards>& shards, std::uint64_t hash) {
    auto& shard = shards[hash % kSeenShards];
    std::lock_guard lock(shard.mutex);
    return shard.hashes.insert(hash).second;
}

void flush_batch(std::vector<State>& batch, std::vector<State>& destination,
                 std::mutex& destination_mutex) {
    if (batch.empty()) {
        return;
    }
    std::lock_guard lock(destination_mutex);
    destination.insert(destination.end(),
                       std::make_move_iterator(batch.begin()),
                       std::make_move_iterator(batch.end()));
    batch.clear();
}

}  // namespace

int main(int argc, char** argv) {
    const int radius = argc > 1 ? std::atoi(argv[1]) : 7;
    const int record_xor = argc > 2 ? std::atoi(argv[2]) : 63;
    const int thread_count = argc > 3 ? std::atoi(argv[3]) : 8;
    if (radius < 0 || record_xor < 0 || thread_count < 1) {
        std::fprintf(stderr, "usage: fast_bfs_parallel [radius] [record_xor] [threads]\n");
        return 2;
    }

    omp_set_dynamic(0);
    omp_set_num_threads(thread_count);

    const State origin = initial_state();
    std::array<SeenShard, kSeenShards> seen;
    for (auto& shard : seen) {
        shard.hashes.reserve(1U << 15);
    }
    mark_seen(seen, state_hash(origin.T));

    std::vector<State> frontier{origin};
    ModeScore unscored;
    unscored.penalty = 999;
    print_candidate(0, state_hash(origin.T), origin, structural_score(origin),
                    greedy_cover(origin), unscored);
    std::uint64_t emitted = 1;

    for (int depth = 1; depth <= radius; ++depth) {
        std::vector<State> next;
        next.reserve(frontier.size() * 8);
        std::mutex next_mutex;
        std::atomic<std::uint64_t> structurally_feasible{0};

#pragma omp parallel
        {
            std::vector<State> batch;
            batch.reserve(kBatchSize);

#pragma omp for schedule(dynamic, 32)
            for (std::ptrdiff_t parent_index = 0;
                 parent_index < static_cast<std::ptrdiff_t>(frontier.size());
                 ++parent_index) {
                const State& parent = frontier[static_cast<std::size_t>(parent_index)];
                for (int destination = 0; destination < kBits; ++destination) {
                    for (int source = 0; source < kBits; ++source) {
                        if (source == destination) {
                            continue;
                        }
                        State candidate = parent;
                        mutate(candidate, destination, source);
                        if (!structural_score(candidate).feasible()) {
                            continue;
                        }
                        structurally_feasible.fetch_add(1, std::memory_order_relaxed);
                        const auto hash = state_hash(candidate.T);
                        if (!mark_seen(seen, hash)) {
                            continue;
                        }
                        batch.push_back(std::move(candidate));
                        if (batch.size() == kBatchSize) {
                            flush_batch(batch, next, next_mutex);
                        }
                    }
                }
            }
            flush_batch(batch, next, next_mutex);
        }

        std::atomic<std::uint64_t> low_xor{0};
#pragma omp parallel for schedule(dynamic, 64)
        for (std::ptrdiff_t index = 0;
             index < static_cast<std::ptrdiff_t>(next.size()); ++index) {
            const State& candidate = next[static_cast<std::size_t>(index)];
            const auto cover = greedy_cover(candidate);
            if (cover.greedy_xor > record_xor) {
                continue;
            }
            low_xor.fetch_add(1, std::memory_order_relaxed);
            const auto hash = state_hash(candidate.T);
#pragma omp critical(rng_candidate_output)
            {
                print_candidate(static_cast<std::uint64_t>(depth), hash, candidate,
                                structural_score(candidate), cover, unscored);
            }
        }

        emitted += low_xor.load(std::memory_order_relaxed);
        std::fprintf(
            stderr,
            "depth=%d parents=%" PRIu64 " structural=%" PRIu64
            " new=%" PRIu64 " total=%" PRIu64 " low_xor=%" PRIu64
            " emitted=%" PRIu64 " threads=%d\n",
            depth, static_cast<std::uint64_t>(frontier.size()),
            structurally_feasible.load(std::memory_order_relaxed),
            static_cast<std::uint64_t>(next.size()), seen_size(seen),
            low_xor.load(std::memory_order_relaxed), emitted, thread_count);
        std::fflush(stderr);
        frontier = std::move(next);
    }
    return 0;
}
