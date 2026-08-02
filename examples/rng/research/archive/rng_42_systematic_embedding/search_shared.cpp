#include <algorithm>
#include <array>
#include <bit>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <random>
#include <string_view>
#include <unordered_map>
#include <unordered_set>
#include <vector>

// Search the 42-leaf systematic embedding with the real depth-two XOR cost.
// A target is a linear form over x[0..31] and q[0..9]=R*x.  Each target may
// choose any representation with at most four leaves; the score is the union
// of all final target gates and all pair gates used by their partitions.

namespace {
constexpr int N = 32;
constexpr int K = 10;
constexpr int M = N + K;
using Row32 = std::uint32_t;
using Row42 = std::uint64_t;
using RRows = std::array<Row32, K>;

std::uint32_t xorshift32(std::uint32_t value) {
    value ^= value >> 13;
    value ^= value << 17;
    value ^= value >> 5;
    return value;
}

std::array<Row32, N> transition_rows() {
    std::array<Row32, N> a{};
    for (int source = 0; source < N; ++source) {
        const auto output = xorshift32(Row32{1} << source);
        for (int target = 0; target < N; ++target) {
            a[target] |= ((output >> target) & 1U) << source;
        }
    }
    return a;
}

Row32 apply_row(Row32 row, const std::array<Row32, N>& matrix) {
    Row32 result = 0;
    while (row) {
        const auto low = row & (0U - row);
        result ^= matrix[std::countr_zero(low)];
        row ^= low;
    }
    return result;
}

struct Option {
    Row42 final_gate = 0;
    std::array<Row42, 2> pairs{};
    std::uint8_t pair_count = 0;
    std::uint8_t weight = 0;
};

struct TargetOptions {
    Row32 semantic = 0;
    std::vector<Option> options;
};

struct CoverScore {
    int valid = 0;
    int xor_count = 10000;
    int final_count = 10000;
    int pair_count = 10000;
    int support_excess = 0;
    int max_weight = 0;
    int total_weight = 0;
};

bool better(const CoverScore& a, const CoverScore& b) {
    if (a.valid != b.valid) return a.valid > b.valid;
    if (!a.valid) {
        if (a.support_excess != b.support_excess) return a.support_excess < b.support_excess;
        if (a.max_weight != b.max_weight) return a.max_weight < b.max_weight;
        return a.total_weight < b.total_weight;
    }
    if (a.xor_count != b.xor_count) return a.xor_count < b.xor_count;
    if (a.pair_count != b.pair_count) return a.pair_count < b.pair_count;
    return a.total_weight < b.total_weight;
}

Row42 coord(Row32 raw, int aux_mask) {
    return Row42{raw} | (Row42{static_cast<unsigned>(aux_mask)} << N);
}

std::vector<Row32> all_aux_combinations(const RRows& rows) {
    std::vector<Row32> result(1U << K);
    for (int mask = 1; mask < (1 << K); ++mask) {
        const int bit = std::countr_zero(static_cast<unsigned>(mask));
        result[mask] = result[mask ^ (1 << bit)] ^ rows[bit];
    }
    return result;
}

void append_option(std::vector<Option>& out, const Option& option) {
    for (const auto& existing : out) {
        if (existing.final_gate != option.final_gate ||
            existing.pair_count != option.pair_count ||
            existing.pairs != option.pairs) {
            continue;
        }
        return;
    }
    out.push_back(option);
}

std::vector<TargetOptions> make_targets(const RRows& rows) {
    const auto a = transition_rows();
    std::vector<Row32> semantics;
    semantics.reserve(N + K);
    for (const auto row : a) semantics.push_back(row);
    for (const auto row : rows) semantics.push_back(apply_row(row, a));

    std::sort(semantics.begin(), semantics.end());
    semantics.erase(std::unique(semantics.begin(), semantics.end()), semantics.end());
    const auto combinations = all_aux_combinations(rows);

    std::vector<TargetOptions> result;
    result.reserve(semantics.size());
    for (const auto semantic : semantics) {
        TargetOptions target;
        target.semantic = semantic;
        std::unordered_set<Row42> seen;
        for (int aux = 0; aux < (1 << K); ++aux) {
            const Row32 raw = semantic ^ combinations[aux];
            const int weight = std::popcount(static_cast<unsigned>(raw)) +
                               std::popcount(static_cast<unsigned>(aux));
            if (weight == 0 || weight > 4) continue;
            const Row42 final_form = coord(raw, aux);
            if (!seen.insert(final_form).second) continue;
            std::vector<int> bits;
            for (Row42 remaining = final_form; remaining; remaining &= remaining - 1) {
                bits.push_back(std::countr_zero(remaining));
            }
            if (bits.size() == 1) {
                append_option(target.options, Option{final_form, {}, 0,
                                                     static_cast<std::uint8_t>(weight)});
            } else if (bits.size() == 2) {
                append_option(target.options, Option{final_form, {final_form, 0}, 1,
                                                     static_cast<std::uint8_t>(weight)});
            } else if (bits.size() == 3) {
                for (int skip = 0; skip < 3; ++skip) {
                    Row42 pair = 0;
                    for (int i = 0; i < 3; ++i) {
                        if (i != skip) pair |= Row42{1} << bits[i];
                    }
                    append_option(target.options, Option{final_form, {pair, 0}, 1,
                                                         static_cast<std::uint8_t>(weight)});
                }
            } else if (bits.size() == 4) {
                for (int mate = 1; mate < 4; ++mate) {
                    const Row42 first = (Row42{1} << bits[0]) | (Row42{1} << bits[mate]);
                    const Row42 second = final_form ^ first;
                    append_option(target.options, Option{final_form, {first, second}, 2,
                                                         static_cast<std::uint8_t>(weight)});
                }
            }
        }
        std::sort(target.options.begin(), target.options.end(), [](const Option& left,
                                                                   const Option& right) {
            if (left.pair_count != right.pair_count) return left.pair_count < right.pair_count;
            if (left.weight != right.weight) return left.weight < right.weight;
            if (left.final_gate != right.final_gate) return left.final_gate < right.final_gate;
            return left.pairs < right.pairs;
        });
        result.push_back(std::move(target));
    }
    return result;
}

struct GateCounts {
    std::unordered_map<Row42, int> count;
    int total = 0;
    void add(Row42 gate) {
        if (!gate) return;
        auto& value = count[gate];
        if (value++ == 0) ++total;
    }
    void remove(Row42 gate) {
        if (!gate) return;
        auto it = count.find(gate);
        if (it == count.end() || it->second <= 0) std::abort();
        if (--it->second == 0) {
            count.erase(it);
            --total;
        }
    }
    int added(const Option& option) const {
        int value = count.contains(option.final_gate) ? 0 : 1;
        for (int i = 0; i < option.pair_count; ++i) {
            value += count.contains(option.pairs[i]) ? 0 : 1;
        }
        return value;
    }
};

void add_option(GateCounts& counts, const Option& option) {
    counts.add(option.final_gate);
    for (int i = 0; i < option.pair_count; ++i) counts.add(option.pairs[i]);
}
void remove_option(GateCounts& counts, const Option& option) {
    counts.remove(option.final_gate);
    for (int i = 0; i < option.pair_count; ++i) counts.remove(option.pairs[i]);
}

CoverScore evaluate(const RRows& rows) {
    const auto a = transition_rows();
    std::vector<Row32> semantics;
    semantics.reserve(N + K);
    for (const auto row : a) semantics.push_back(row);
    for (const auto row : rows) semantics.push_back(apply_row(row, a));
    std::sort(semantics.begin(), semantics.end());
    semantics.erase(std::unique(semantics.begin(), semantics.end()), semantics.end());
    const auto combinations = all_aux_combinations(rows);

    CoverScore support;
    for (const auto semantic : semantics) {
        int minimum = M + 1;
        for (int aux = 0; aux < (1 << K); ++aux) {
            const Row32 raw = semantic ^ combinations[aux];
            minimum = std::min(minimum,
                std::popcount(static_cast<unsigned>(raw)) +
                std::popcount(static_cast<unsigned>(aux)));
        }
        support.support_excess += std::max(0, minimum - 4);
        support.max_weight = std::max(support.max_weight, minimum);
        support.total_weight += minimum;
    }
    if (support.support_excess) return support;

    const auto targets = make_targets(rows);
    for (const auto& target : targets) {
        if (target.options.empty()) {
            CoverScore result;
            result.support_excess = 100;
            return result;
        }
    }

    CoverScore best;
    std::uint64_t row_hash = 0x9e3779b97f4a7c15ULL;
    for (const auto row : rows) {
        row_hash ^= row + 0x9e3779b97f4a7c15ULL + (row_hash << 6) + (row_hash >> 2);
    }
    std::mt19937_64 option_random(row_hash);
    constexpr int kRestarts = 32;
    for (int restart = 0; restart < kRestarts; ++restart) {
        std::vector<int> selected(targets.size(), 0);
        std::vector<std::size_t> order(targets.size());
        for (std::size_t i = 0; i < order.size(); ++i) order[i] = i;
        if (restart) std::shuffle(order.begin(), order.end(), option_random);
        GateCounts counts;
        for (const auto index : order) {
            const auto& options = targets[index].options;
            int choice = restart
                ? static_cast<int>(option_random() % options.size())
                : 0;
            if (!restart) {
                int best_added = 100;
                for (int i = 0; i < static_cast<int>(options.size()); ++i) {
                    const int added = counts.added(options[i]);
                    if (added < best_added ||
                        (added == best_added && options[i].weight < options[choice].weight)) {
                        best_added = added;
                        choice = i;
                    }
                }
            }
            selected[index] = choice;
            add_option(counts, options[choice]);
        }
        for (int pass = 0; pass < 12; ++pass) {
            bool changed = false;
            if (restart) std::shuffle(order.begin(), order.end(), option_random);
            else if (pass & 1) std::reverse(order.begin(), order.end());
            for (const auto index : order) {
                const auto& options = targets[index].options;
                remove_option(counts, options[selected[index]]);
                int choice = selected[index];
                int cost = 100;
                for (int i = 0; i < static_cast<int>(options.size()); ++i) {
                    const int added = counts.added(options[i]);
                    const int weight_bias = options[i].weight;
                    if (added < cost || (added == cost && weight_bias < options[choice].weight)) {
                        cost = added;
                        choice = i;
                    }
                }
                if (choice != selected[index]) changed = true;
                selected[index] = choice;
                add_option(counts, options[choice]);
            }
            if (!changed) break;
        }
        CoverScore score;
        score.valid = 1;
        score.xor_count = counts.total;
        score.final_count = static_cast<int>(targets.size());
        score.pair_count = score.xor_count - score.final_count;
        score.max_weight = support.max_weight;
        for (std::size_t index = 0; index < targets.size(); ++index) {
            score.total_weight += targets[index].options[selected[index]].weight;
        }
        if (better(score, best)) best = score;
    }
    return best;
}

void print_rows(const RRows& rows) {
    for (int i = 0; i < K; ++i) std::printf("%s%08x", i ? "," : "", rows[i]);
}

std::vector<Row32> pool(const std::array<Row32, N>& a) {
    std::unordered_set<Row32> unique;
    for (int left = 0; left < N; ++left) {
        for (int right = left + 1; right < N; ++right) {
            unique.insert((Row32{1} << left) | (Row32{1} << right));
        }
    }
    for (const auto row : a) {
        std::vector<int> bits;
        for (auto remaining = row; remaining; remaining &= remaining - 1) {
            bits.push_back(std::countr_zero(remaining));
        }
        for (int i = 0; i < static_cast<int>(bits.size()); ++i) {
            for (int j = i + 1; j < static_cast<int>(bits.size()); ++j) {
                for (int k = j + 1; k < static_cast<int>(bits.size()); ++k) {
                    unique.insert((Row32{1} << bits[i]) | (Row32{1} << bits[j]) |
                                  (Row32{1} << bits[k]));
                    for (int l = k + 1; l < static_cast<int>(bits.size()); ++l) {
                        unique.insert((Row32{1} << bits[i]) | (Row32{1} << bits[j]) |
                                      (Row32{1} << bits[k]) | (Row32{1} << bits[l]));
                    }
                }
            }
        }
    }
    return {unique.begin(), unique.end()};
}

RRows parse_start() {
    return {0x00080004U, 0x00220010U, 0x21001080U, 0x908c4042U,
            0x00108000U, 0x02200100U, 0x0c620210U, 0x00440020U,
            0x80044002U, 0x40022001U};
}

}  // namespace

int main(int argc, char** argv) {
    if (argc > 1 && std::string_view(argv[1]) == "neighborhood") {
        const auto candidates = pool(transition_rows());
        RRows current = parse_start();
        CoverScore score = evaluate(current);
        std::printf("round=0 xor=%d pair=%d total=%d pool=%zu R=",
                    score.xor_count, score.pair_count, score.total_weight,
                    candidates.size());
        print_rows(current); std::printf("\n"); std::fflush(stdout);
        for (int round = 1; round <= 30; ++round) {
            RRows round_best = current;
            CoverScore round_score = score;
            for (int row = 0; row < K; ++row) {
                const auto consider = [&](Row32 replacement) {
                    if (!replacement || replacement == current[row]) return;
                    RRows proposal = current;
                    proposal[row] = replacement;
                    if (std::count(proposal.begin(), proposal.end(), replacement) != 1) return;
                    const auto candidate_score = evaluate(proposal);
                    if (better(candidate_score, round_score)) {
                        round_best = proposal;
                        round_score = candidate_score;
                    }
                };
                for (const auto replacement : candidates) consider(replacement);
                for (int bit = 0; bit < N; ++bit) consider(current[row] ^ (Row32{1} << bit));
                for (int other = 0; other < K; ++other) {
                    if (other != row) consider(current[row] ^ current[other]);
                }
            }
            if (!better(round_score, score)) break;
            current = round_best;
            score = round_score;
            std::printf("round=%d valid=%d xor=%d pair=%d excess=%d max=%d total=%d R=",
                        round, score.valid, score.xor_count, score.pair_count,
                        score.support_excess, score.max_weight, score.total_weight);
            print_rows(current); std::printf("\n"); std::fflush(stdout);
            if (score.valid && score.xor_count <= 61) return 0;
        }
        return score.valid && score.xor_count <= 61 ? 0 : 2;
    }
    const std::uint64_t seed = argc > 1 ? std::strtoull(argv[1], nullptr, 0) : 0x42;
    const std::uint64_t steps = argc > 2 ? std::strtoull(argv[2], nullptr, 0) : 1000000;
    const std::uint64_t restart_period = argc > 3 ? std::strtoull(argv[3], nullptr, 0) : 50000;
    const auto a = transition_rows();
    const auto candidates = pool(a);
    std::mt19937_64 random(seed);
    std::uniform_real_distribution<double> unit(0.0, 1.0);

    RRows global = parse_start();
    CoverScore global_score = evaluate(global);
    std::printf("best step=0 valid=%d xor=%d pair=%d excess=%d max=%d total=%d R=",
                global_score.valid, global_score.xor_count, global_score.pair_count,
                global_score.support_excess, global_score.max_weight, global_score.total_weight);
    print_rows(global); std::printf("\n"); std::fflush(stdout);
    RRows current = global;
    CoverScore current_score = global_score;
    for (std::uint64_t step = 1; step <= steps; ++step) {
        if (restart_period && step % restart_period == 0) {
            current = global;
            for (int p = 0; p < 3; ++p) current[random() % K] = candidates[random() % candidates.size()];
            current_score = evaluate(current);
        }
        RRows proposal = current;
        const int row = static_cast<int>(random() % K);
        const auto mode = random() % 100;
        if (mode < 70) proposal[row] = candidates[random() % candidates.size()];
        else if (mode < 90) proposal[row] ^= Row32{1} << (random() % N);
        else {
            int other = static_cast<int>(random() % (K - 1));
            other += other >= row;
            proposal[row] ^= proposal[other];
        }
        if (!proposal[row] || std::find(proposal.begin(), proposal.end(), proposal[row]) != proposal.begin() + row) continue;
        const CoverScore ps = evaluate(proposal);
        if (better(ps, global_score)) {
            global = proposal; global_score = ps;
            std::printf("best step=%llu valid=%d xor=%d pair=%d excess=%d max=%d total=%d R=",
                        static_cast<unsigned long long>(step), ps.valid, ps.xor_count,
                        ps.pair_count, ps.support_excess, ps.max_weight, ps.total_weight);
            print_rows(global); std::printf("\n"); std::fflush(stdout);
            if (ps.valid && ps.xor_count <= 61) return 0;
        }
        const double phase = restart_period ? double(step % restart_period) / restart_period
                                            : double(step) / steps;
        const double temperature = 3000.0 * std::pow(0.001, phase) + 0.5;
        auto energy = [](const CoverScore& s) {
            if (!s.valid) return 90000.0 + 2500.0 * s.support_excess +
                                  100.0 * s.max_weight + s.total_weight;
            return 1000.0 * s.xor_count + s.total_weight;
        };
        const double delta = energy(ps) - energy(current_score);
        if (delta <= 0.0 || unit(random) < std::exp(-delta / temperature)) {
            current = proposal; current_score = ps;
        }
    }
    std::printf("final valid=%d xor=%d\n", global_score.valid, global_score.xor_count);
    return global_score.valid && global_score.xor_count <= 61 ? 0 : 2;
}
