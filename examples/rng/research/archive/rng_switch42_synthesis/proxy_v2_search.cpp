#include <algorithm>
#include <array>
#include <bit>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <random>
#include <set>
#include <tuple>
#include <unordered_map>
#include <vector>

namespace {

constexpr unsigned visible = 32;
constexpr unsigned hidden = 10;
constexpr unsigned state_bits = visible + hidden;
constexpr std::uint64_t visible_mask = 0xffff'ffffULL;

std::uint32_t xorshift32(std::uint32_t value) {
    value ^= value >> 13;
    value ^= value << 17;
    value ^= value >> 5;
    return value;
}

std::array<std::uint32_t, visible> transition_rows() {
    std::array<std::uint32_t, visible> rows{};
    for (unsigned source = 0; source < visible; ++source) {
        const auto output = xorshift32(std::uint32_t{1} << source);
        for (unsigned target = 0; target < visible; ++target) {
            if ((output >> target) & 1u) rows[target] |= std::uint32_t{1} << source;
        }
    }
    return rows;
}

struct State {
    std::array<std::uint16_t, visible> x{};
    std::array<std::uint64_t, hidden> d{};
};

struct PatternOption {
    std::array<std::uint16_t, 3> blocks{};
    unsigned block_count = 0;
    unsigned final_cost = 0;
};

using PatternTable = std::array<std::vector<PatternOption>, 10>;

void build_patterns_visit(
    unsigned weight,
    unsigned index,
    std::array<std::uint16_t, 3>& blocks,
    unsigned count,
    std::vector<PatternOption>& output
) {
    if (index == weight) {
        PatternOption option;
        option.blocks = blocks;
        option.block_count = count;
        option.final_cost = count == 1 ? 0 : (count == 2 ? 3 : 12);
        output.push_back(option);
        return;
    }
    for (unsigned block = 0; block < count; ++block) {
        if (std::popcount(blocks[block]) == 3) continue;
        blocks[block] |= std::uint16_t{1} << index;
        build_patterns_visit(weight, index + 1, blocks, count, output);
        blocks[block] ^= std::uint16_t{1} << index;
    }
    if (count < 3) {
        blocks[count] = std::uint16_t{1} << index;
        build_patterns_visit(weight, index + 1, blocks, count + 1, output);
        blocks[count] = 0;
    }
}

PatternTable build_patterns() {
    PatternTable result;
    for (unsigned weight = 2; weight <= 9; ++weight) {
        std::array<std::uint16_t, 3> blocks{};
        build_patterns_visit(weight, 0, blocks, 0, result[weight]);
    }
    return result;
}

struct Score {
    int unsupported = 0;
    int active_hidden = 0;
    int distinct_targets = 0;
    int maximum = 0;
    int total_weight = 0;
    int excess4 = 0;
    int old_proxy = 1'000'000;
    double fractional_logic = 1e9;
    double fractional_total = 1e9;

    auto key() const {
        return std::tuple(
            unsupported,
            static_cast<std::int64_t>(std::llround(fractional_total * 1000.0)),
            old_proxy,
            distinct_targets,
            total_weight
        );
    }
};

bool operator<(const Score& left, const Score& right) { return left.key() < right.key(); }

class Search {
public:
    explicit Search(std::uint64_t seed)
        : generator_(seed), a_(transition_rows()), patterns_(build_patterns()) {
        for (unsigned mask = 0; mask < (1u << hidden); ++mask) {
            if (std::popcount(mask) <= 3) x_masks_.push_back(static_cast<std::uint16_t>(mask));
        }
    }

    Score evaluate(const State& state) const {
        Score score;
        const auto active = active_hidden(state);
        score.active_hidden = std::popcount(active);
        const std::uint64_t projection = visible_mask | (std::uint64_t{active} << visible);

        std::array<std::uint64_t, visible> output{};
        for (unsigned row = 0; row < visible; ++row) {
            output[row] = ((std::uint64_t{1} << row) |
                           (std::uint64_t{state.x[row]} << visible)) & projection;
        }
        std::array<std::uint64_t, visible> top{};
        for (unsigned row = 0; row < visible; ++row) {
            for (auto sources = a_[row]; sources; sources &= sources - 1) {
                top[row] ^= output[std::countr_zero(sources)];
            }
            for (auto correction = state.x[row]; correction; correction &= correction - 1) {
                top[row] ^= state.d[std::countr_zero(correction)];
            }
            top[row] &= projection;
        }

        std::vector<std::uint64_t> targets;
        targets.reserve(visible * 2 + hidden);
        for (const auto row : output) if (std::popcount(row) >= 2) targets.push_back(row);
        for (const auto row : top) if (std::popcount(row) >= 2) targets.push_back(row);
        for (unsigned index = 0; index < hidden; ++index) {
            if ((active >> index) & 1u) {
                const auto row = state.d[index] & projection;
                if (std::popcount(row) >= 2) targets.push_back(row);
            }
        }
        std::sort(targets.begin(), targets.end());
        targets.erase(std::unique(targets.begin(), targets.end()), targets.end());
        score.distinct_targets = static_cast<int>(targets.size());

        std::unordered_map<std::uint64_t, unsigned> frequency;
        frequency.reserve(2048);
        std::vector<std::array<unsigned, 9>> supports(targets.size());
        std::vector<unsigned> weights(targets.size());
        for (unsigned target_index = 0; target_index < targets.size(); ++target_index) {
            const auto target = targets[target_index];
            const unsigned weight = std::popcount(target);
            weights[target_index] = weight;
            score.maximum = std::max(score.maximum, static_cast<int>(weight));
            score.total_weight += weight;
            score.excess4 += std::max(0, static_cast<int>(weight) - 4);
            if (weight > 9) {
                score.unsupported += static_cast<int>(weight) - 9;
                continue;
            }
            unsigned at = 0;
            for (auto value = target; value; value &= value - 1) {
                supports[target_index][at++] = std::countr_zero(value);
            }
            if (weight <= 8) {
                for (unsigned i = 0; i < weight; ++i) {
                    for (unsigned j = i + 1; j < weight; ++j) {
                        ++frequency[(std::uint64_t{1} << supports[target_index][i]) |
                                    (std::uint64_t{1} << supports[target_index][j])];
                    }
                }
            }
            if (weight >= 3) {
                for (unsigned i = 0; i < weight; ++i) {
                    for (unsigned j = i + 1; j < weight; ++j) {
                        for (unsigned k = j + 1; k < weight; ++k) {
                            ++frequency[(std::uint64_t{1} << supports[target_index][i]) |
                                        (std::uint64_t{1} << supports[target_index][j]) |
                                        (std::uint64_t{1} << supports[target_index][k])];
                        }
                    }
                }
            }
        }

        double logic = 0.0;
        if (score.unsupported == 0) {
            for (unsigned target_index = 0; target_index < targets.size(); ++target_index) {
                const unsigned weight = weights[target_index];
                double best = std::numeric_limits<double>::infinity();
                for (const auto& option : patterns_[weight]) {
                    double cost = option.final_cost;
                    for (unsigned block_index = 0; block_index < option.block_count; ++block_index) {
                        const auto positional = option.blocks[block_index];
                        const unsigned block_weight = std::popcount(positional);
                        if (block_weight == 1) continue;
                        std::uint64_t group = 0;
                        for (auto bits = positional; bits; bits &= bits - 1) {
                            group |= std::uint64_t{1} << supports[target_index][std::countr_zero(bits)];
                        }
                        const auto found = frequency.find(group);
                        const unsigned uses = found == frequency.end() ? 1 : found->second;
                        cost += static_cast<double>(block_weight == 2 ? 3 : 12) / uses;
                    }
                    best = std::min(best, cost);
                }
                logic += best;
            }
        } else {
            logic = 10'000.0 + 1000.0 * score.unsupported;
        }
        score.fractional_logic = logic;
        score.fractional_total = 198.0 + 5.0 * score.active_hidden + logic;
        score.old_proxy = 198 + 5 * score.active_hidden + 3 * score.distinct_targets +
                          10 * score.excess4;
        return score;
    }

    void initialize(State& state, unsigned restart) {
        constexpr std::array<std::uint16_t, visible> current_x{
            0x010,0x022,0x040,0x004,0x008,0x090,0x0e0,0x040,
            0x100,0x200,0x080,0x044,0x101,0x100,0x200,0x004,
            0x008,0x011,0x022,0x040,0x004,0x108,0x210,0x020,
            0x040,0x100,0x300,0x280,0x000,0x000,0x100,0x000,
        };
        constexpr std::array<std::uint64_t, hidden> current_d{
            0x20040020001,0x20000044002,0x00000110008,0x00100220010,
            0x02200040020,0x08000880040,0x00401100080,0x02000800400,
            0x20084002000,0x08008404000,
        };
        constexpr std::array<std::uint16_t, visible> pruned_x{
            0x000,0x000,0x001,0x010,0x084,0x002,0x001,0x001,
            0x000,0x200,0x000,0x001,0x000,0x204,0x000,0x000,
            0x000,0x080,0x206,0x001,0x010,0x004,0x006,0x000,
            0x001,0x010,0x004,0x000,0x000,0x000,0x284,0x000,
        };
        constexpr std::array<std::uint64_t, hidden> pruned_d{
            0x00001100080,0x20004840000,0x20204400000,0x00000000000,
            0x01002200100,0x00000000000,0x00000000000,0x00200022000,
            0x00000000000,0x20400404000,
        };
        constexpr std::array<std::uint16_t, visible> beam6_x{
            0x002,0x001,0x020,0x010,0x008,0x002,0x000,0x020,
            0x000,0x008,0x000,0x000,0x004,0x000,0x000,0x000,
            0x000,0x002,0x001,0x020,0x010,0x008,0x002,0x000,
            0x020,0x004,0x008,0x000,0x000,0x000,0x000,0x000,
        };
        constexpr std::array<std::uint64_t, hidden> beam6_d{
            0x00000084042,0x00100440020,0x00042003000,0x00204400200,
            0x00800300100,0x01001100080,0x00000000000,0x00000000000,
            0x00000000000,0x00000000000,
        };
        if (restart % 4 == 0) {
            state.x = {};
            state.d = {};
        } else if (restart % 4 == 1) {
            state.x = beam6_x;
            state.d = beam6_d;
        } else if (restart % 4 == 2) {
            state.x = pruned_x;
            state.d = pruned_d;
        } else {
            state.x = current_x;
            state.d = current_d;
        }
        const unsigned kicks = restart < 4 ? 0 : 4 + restart % 17;
        for (unsigned kick = 0; kick < kicks; ++kick) mutate(state, true);
    }

    void mutate(State& state, bool hot = false) {
        const unsigned kind = generator_() % 100;
        if (kind < 52) {
            const unsigned row = generator_() % visible;
            if ((generator_() % 100) < 65) {
                unsigned bit = generator_() % hidden;
                auto next = static_cast<std::uint16_t>(state.x[row] ^ (std::uint16_t{1} << bit));
                if (std::popcount(next) <= 3) state.x[row] = next;
            } else {
                state.x[row] = x_masks_[generator_() % x_masks_.size()];
            }
            return;
        }
        if (kind < 88) {
            auto& row = state.d[generator_() % hidden];
            const unsigned choice = generator_() % 100;
            if (choice < 12) {
                row = 0;
            } else if (choice < 25) {
                row = random_sparse_row(hot ? 5 : 12);
            } else {
                const unsigned bit = generator_() % state_bits;
                if ((row >> bit) & 1u) {
                    row ^= std::uint64_t{1} << bit;
                } else {
                    if (std::popcount(row) == 4) {
                        const unsigned remove = nth_set_bit(row, generator_() % 4);
                        row ^= std::uint64_t{1} << remove;
                    }
                    row |= std::uint64_t{1} << bit;
                }
            }
            return;
        }
        const unsigned column = generator_() % hidden;
        const auto bit = std::uint16_t{1} << column;
        if ((generator_() % 100) < 58) {
            state.d[column] = 0;
            for (auto& value : state.x) value &= ~bit;
            const std::uint64_t high_bit = std::uint64_t{1} << (visible + column);
            for (auto& value : state.d) value &= ~high_bit;
        } else {
            state.d[column] = random_sparse_row(0);
            for (unsigned row = 0; row < visible; ++row) {
                if ((generator_() % 100) < 10) {
                    auto next = static_cast<std::uint16_t>(state.x[row] ^ bit);
                    if (std::popcount(next) <= 3) state.x[row] = next;
                }
            }
        }
    }

    Score polish(State& state, unsigned passes = 2) {
        auto current = evaluate(state);
        for (unsigned pass = 0; pass < passes; ++pass) {
            bool changed = false;
            std::vector<unsigned> order(visible + hidden);
            for (unsigned i = 0; i < order.size(); ++i) order[i] = i;
            std::shuffle(order.begin(), order.end(), generator_);
            for (const auto coordinate : order) {
                State best_state = state;
                Score best = current;
                if (coordinate < visible) {
                    const unsigned row = coordinate;
                    std::array<std::uint16_t, 48> candidates{};
                    unsigned count = 0;
                    candidates[count++] = 0;
                    candidates[count++] = state.x[row];
                    for (unsigned bit = 0; bit < hidden; ++bit) {
                        const auto toggled = static_cast<std::uint16_t>(state.x[row] ^ (1u << bit));
                        if (std::popcount(toggled) <= 3) candidates[count++] = toggled;
                    }
                    while (count < candidates.size()) {
                        candidates[count++] = x_masks_[generator_() % x_masks_.size()];
                    }
                    for (const auto value : candidates) {
                        State proposal = state;
                        proposal.x[row] = value;
                        const auto score = evaluate(proposal);
                        if (score < best) { best = score; best_state = proposal; }
                    }
                } else {
                    const unsigned row = coordinate - visible;
                    std::vector<std::uint64_t> candidates{0, state.d[row]};
                    for (auto bits = state.d[row]; bits; bits &= bits - 1) {
                        candidates.push_back(state.d[row] ^ (bits & (0 - bits)));
                    }
                    for (unsigned sample = 0; sample < 72; ++sample) {
                        auto value = state.d[row];
                        const unsigned bit = generator_() % state_bits;
                        value ^= std::uint64_t{1} << bit;
                        if (std::popcount(value) <= 4) candidates.push_back(value);
                    }
                    for (const auto value : candidates) {
                        State proposal = state;
                        proposal.d[row] = value;
                        const auto score = evaluate(proposal);
                        if (score < best) { best = score; best_state = proposal; }
                    }
                }
                if (best < current) {
                    state = best_state;
                    current = best;
                    changed = true;
                }
            }
            if (!changed) break;
        }
        return current;
    }

    std::vector<State> guided_add_hidden(
        const State& input,
        unsigned group_limit,
        unsigned keep
    ) {
        State base = input;
        const auto active = active_hidden(base);
        unsigned column = hidden;
        for (unsigned index = 0; index < hidden; ++index) {
            if (((active >> index) & 1u) == 0) {
                column = index;
                break;
            }
        }
        if (column == hidden) return {};

        const auto x_bit = static_cast<std::uint16_t>(1u << column);
        const auto state_bit = std::uint64_t{1} << (visible + column);
        for (auto& row : base.x) row &= ~x_bit;
        for (auto& row : base.d) row &= ~state_bit;
        base.d[column] = 0;

        const auto base_active = active_hidden(base);
        const std::uint64_t projection = visible_mask | (std::uint64_t{base_active} << visible);
        std::array<std::uint64_t, visible> output{};
        for (unsigned row = 0; row < visible; ++row) {
            output[row] = ((std::uint64_t{1} << row) |
                           (std::uint64_t{base.x[row]} << visible)) & projection;
        }
        std::array<std::uint64_t, visible> top{};
        for (unsigned row = 0; row < visible; ++row) {
            for (auto sources = a_[row]; sources; sources &= sources - 1) {
                top[row] ^= output[std::countr_zero(sources)];
            }
            for (auto correction = base.x[row]; correction; correction &= correction - 1) {
                top[row] ^= base.d[std::countr_zero(correction)];
            }
            top[row] &= projection;
        }

        std::set<std::uint64_t> distinct;
        for (const auto row : output) if (std::popcount(row) >= 2) distinct.insert(row);
        for (const auto row : top) if (std::popcount(row) >= 2) distinct.insert(row);
        for (unsigned index = 0; index < hidden; ++index) {
            if ((base_active >> index) & 1u) {
                const auto row = base.d[index] & projection;
                if (std::popcount(row) >= 2) distinct.insert(row);
            }
        }

        std::unordered_map<std::uint64_t, unsigned> occurrence;
        occurrence.reserve(8192);
        for (const auto target : distinct) {
            for (auto subset = target; subset; subset = (subset - 1) & target) {
                const auto weight = std::popcount(subset);
                if (weight >= 2 && weight <= 4) ++occurrence[subset];
            }
        }
        std::vector<std::pair<std::uint64_t, unsigned>> groups(
            occurrence.begin(), occurrence.end()
        );
        std::sort(groups.begin(), groups.end(), [](const auto& left, const auto& right) {
            const auto left_key = std::tuple(
                -static_cast<int>(left.second), std::popcount(left.first), left.first
            );
            const auto right_key = std::tuple(
                -static_cast<int>(right.second), std::popcount(right.first), right.first
            );
            return left_key < right_key;
        });
        if (groups.size() > group_limit) groups.resize(group_limit);

        std::vector<std::pair<Score, State>> pool;
        pool.reserve(groups.size());
        for (const auto [group, count] : groups) {
            (void)count;
            State proposal = base;
            proposal.d[column] = group;
            const int group_weight = std::popcount(group);
            for (unsigned row = 0; row < visible; ++row) {
                if (std::popcount(proposal.x[row]) >= 3) continue;
                const int overlap = std::popcount(top[row] & group);
                if (2 * overlap > group_weight) proposal.x[row] |= x_bit;
            }
            pool.emplace_back(evaluate(proposal), proposal);
        }
        const auto prekeep = std::min<std::size_t>(std::max(keep * 4u, 16u), pool.size());
        std::partial_sort(
            pool.begin(), pool.begin() + prekeep, pool.end(),
            [](const auto& left, const auto& right) { return left.first < right.first; }
        );
        pool.resize(prekeep);

        for (auto& [score, state] : pool) {
            for (unsigned pass = 0; pass < 3; ++pass) {
                bool changed = false;
                std::array<unsigned, visible> order{};
                for (unsigned row = 0; row < visible; ++row) order[row] = row;
                std::shuffle(order.begin(), order.end(), generator_);
                for (const auto row : order) {
                    if ((state.x[row] & x_bit) == 0 && std::popcount(state.x[row]) >= 3) continue;
                    State proposal = state;
                    proposal.x[row] ^= x_bit;
                    const auto candidate = evaluate(proposal);
                    if (candidate < score) {
                        state = proposal;
                        score = candidate;
                        changed = true;
                    }
                }
                if (!changed) break;
            }
        }
        std::sort(pool.begin(), pool.end(), [](const auto& left, const auto& right) {
            return left.first < right.first;
        });
        if (pool.size() > keep) pool.resize(keep);
        std::vector<State> result;
        for (auto& item : pool) result.push_back(std::move(item.second));
        return result;
    }

    void print(const State& state, const Score& score, const char* label) const {
        std::cout << std::fixed << std::setprecision(3)
                  << label << " unsupported=" << score.unsupported
                  << " active_hidden=" << score.active_hidden
                  << " targets=" << score.distinct_targets
                  << " max=" << score.maximum
                  << " excess4=" << score.excess4
                  << " fractional_logic=" << score.fractional_logic
                  << " fractional_total=" << score.fractional_total
                  << " old_proxy=" << score.old_proxy
                  << " total_weight=" << score.total_weight << " X=";
        for (unsigned i = 0; i < visible; ++i) {
            if (i) std::cout << ',';
            std::cout << std::hex << std::setw(3) << std::setfill('0') << state.x[i];
        }
        std::cout << " D=";
        for (unsigned i = 0; i < hidden; ++i) {
            if (i) std::cout << ',';
            std::cout << std::hex << std::setw(11) << std::setfill('0') << state.d[i];
        }
        std::cout << std::dec << '\n';
    }

private:
    std::uint16_t active_hidden(const State& state) const {
        std::uint16_t active = 0;
        bool changed = true;
        while (changed) {
            changed = false;
            const std::uint64_t sources = visible_mask | (std::uint64_t{active} << visible);
            for (unsigned row = 0; row < hidden; ++row) {
                if (((active >> row) & 1u) == 0 && (state.d[row] & sources) != 0) {
                    active |= std::uint16_t{1} << row;
                    changed = true;
                }
            }
        }
        return active;
    }

    unsigned nth_set_bit(std::uint64_t value, unsigned index) const {
        while (index--) value &= value - 1;
        return std::countr_zero(value);
    }

    std::uint64_t random_sparse_row(unsigned zero_percent) {
        if (generator_() % 100 < zero_percent) return 0;
        const unsigned weight = 1 + generator_() % 4;
        std::uint64_t row = 0;
        while (std::popcount(row) < static_cast<int>(weight)) {
            row |= std::uint64_t{1} << (generator_() % state_bits);
        }
        return row;
    }

    mutable std::mt19937_64 generator_;
    std::array<std::uint32_t, visible> a_{};
    PatternTable patterns_;
    std::vector<std::uint16_t> x_masks_;
};

}  // namespace

int main(int argc, char** argv) {
    std::uint64_t iterations = 100'000;
    unsigned restarts = 4;
    std::uint64_t seed = 20260802051ULL;
    if (argc > 1) iterations = std::stoull(argv[1]);
    if (argc > 2) restarts = static_cast<unsigned>(std::stoul(argv[2]));
    if (argc > 3) seed = std::stoull(argv[3]);

    Search search(seed);
    if (argc > 4 && std::string(argv[4]) == "beam") {
        unsigned beam_width = argc > 5 ? static_cast<unsigned>(std::stoul(argv[5])) : 6;
        unsigned group_limit = argc > 6 ? static_cast<unsigned>(std::stoul(argv[6])) : 768;
        State natural;
        std::vector<State> beam{natural};
        auto best_state = natural;
        auto best_score = search.evaluate(natural);
        search.print(best_state, best_score, "beam0");
        for (unsigned depth = 1; depth <= hidden; ++depth) {
            std::vector<std::pair<Score, State>> next;
            for (const auto& state : beam) {
                for (auto candidate : search.guided_add_hidden(state, group_limit, beam_width)) {
                    next.emplace_back(search.evaluate(candidate), std::move(candidate));
                }
            }
            if (next.empty()) break;
            std::sort(next.begin(), next.end(), [](const auto& left, const auto& right) {
                return left.first < right.first;
            });
            if (next.size() > beam_width) next.resize(beam_width);
            beam.clear();
            for (auto& item : next) beam.push_back(std::move(item.second));
            if (next.front().first < best_score) {
                best_score = next.front().first;
                best_state = beam.front();
            }
            search.print(beam.front(), next.front().first, "beam");
        }
        search.print(best_state, best_score, "final");
        return 0;
    }
    State global_state;
    Score global_score;
    for (unsigned restart = 0; restart < restarts; ++restart) {
        State current;
        search.initialize(current, restart);
        auto current_score = restart % 4 == 1
            ? search.evaluate(current)
            : search.polish(current, 1);
        if (current_score < global_score) {
            global_state = current;
            global_score = current_score;
            search.print(global_state, global_score, "best");
        }
        std::mt19937_64 acceptance(seed ^ (0x9e3779b97f4a7c15ULL * (restart + 1)));
        std::uniform_real_distribution<double> unit(0.0, 1.0);
        State basin_best = current;
        Score basin_score = current_score;
        for (std::uint64_t iteration = 0; iteration < iterations; ++iteration) {
            State proposal = current;
            search.mutate(proposal);
            const auto proposal_score = search.evaluate(proposal);
            const double progress = static_cast<double>(iteration) / iterations;
            const double temperature = 12.0 * std::pow(0.02, progress) + 0.02;
            const double delta = proposal_score.fractional_total - current_score.fractional_total +
                                 1000.0 * (proposal_score.unsupported - current_score.unsupported);
            if (delta <= 0.0 || unit(acceptance) < std::exp(-delta / temperature)) {
                current = proposal;
                current_score = proposal_score;
            }
            if (current_score < basin_score) {
                basin_best = current;
                basin_score = current_score;
            }
            if (current_score < global_score) {
                global_state = current;
                global_score = current_score;
                search.print(global_state, global_score, "best");
            }
            if ((iteration + 1) % 25'000 == 0) {
                current = basin_best;
                current_score = search.polish(current, 1);
                basin_best = current;
                basin_score = current_score;
                if (current_score < global_score) {
                    global_state = current;
                    global_score = current_score;
                    search.print(global_state, global_score, "best");
                }
            }
        }
        current = basin_best;
        current_score = search.polish(current, 2);
        if (current_score < global_score) {
            global_state = current;
            global_score = current_score;
            search.print(global_state, global_score, "best");
        }
    }
    search.print(global_state, global_score, "final");
    return 0;
}
