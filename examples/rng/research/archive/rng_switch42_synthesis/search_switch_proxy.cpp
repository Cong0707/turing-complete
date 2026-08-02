#include <algorithm>
#include <array>
#include <bit>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <random>
#include <set>
#include <tuple>
#include <unordered_set>
#include <vector>

namespace {

constexpr unsigned visible = 32;
constexpr unsigned max_hidden = 10;

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
            if ((output >> target) & 1u) {
                rows[target] |= std::uint32_t{1} << source;
            }
        }
    }
    return rows;
}

struct State {
    std::array<std::uint16_t, visible> x{};
    std::array<std::uint64_t, max_hidden> d{};
};

struct SparseScore {
    int unsupported = 0;
    int maximum = 0;
    int weight_five = 0;
    int finals = 0;
    int optimistic_logic_gate = 0;
    int budget_defect = 0;
    int total_weight = 0;

    auto key() const {
        return std::tie(
            unsupported, budget_defect, optimistic_logic_gate,
            weight_five, maximum, total_weight
        );
    }
};

bool operator<(const SparseScore& left, const SparseScore& right) {
    return left.key() < right.key();
}

bool operator==(const SparseScore& left, const SparseScore& right) {
    return left.key() == right.key();
}

void account(SparseScore& score, int weight) {
    score.unsupported += std::max(0, weight - 5);
    score.maximum = std::max(score.maximum, weight);
    score.total_weight += weight;
}

class Search {
public:
    Search(unsigned hidden, std::uint64_t seed)
        : hidden_(hidden), bits_(visible + hidden), generator_(seed), a_(transition_rows()) {
        if (hidden_ == 0 || hidden_ > max_hidden) {
            throw std::runtime_error("hidden must be in 1..10");
        }
        build_domains();
        build_column_users();
    }

    void set_known_start(State& state) const {
        if (hidden_ != 10) {
            random_start(state);
            return;
        }
        constexpr std::array<std::uint16_t, visible> known_x{
            0x010, 0x122, 0x040, 0x004, 0x008, 0x090, 0x020, 0x040,
            0x108, 0x200, 0x080, 0x044, 0x101, 0x100, 0x200, 0x004,
            0x008, 0x011, 0x022, 0x040, 0x004, 0x008, 0x210, 0x020,
            0x040, 0x100, 0x200, 0x280, 0x000, 0x000, 0x100, 0x200,
        };
        constexpr std::array<std::uint64_t, max_hidden> known_d{
            0x20040020001ULL, 0x10400004002ULL, 0x00800110008ULL,
            0x00100220010ULL, 0x08200040020ULL, 0x04400080040ULL,
            0x00401100080ULL, 0x0a000800400ULL, 0x20004002000ULL,
            0x08008404000ULL,
        };
        state.x = known_x;
        state.d = known_d;
    }

    void random_start(State& state) const {
        for (auto& value : state.x) {
            value = x_domain_[generator_() % x_domain_.size()];
        }
        for (unsigned index = 0; index < hidden_; ++index) {
            state.d[index] = d_domain_[generator_() % d_domain_.size()];
        }
        for (unsigned index = hidden_; index < max_hidden; ++index) {
            state.d[index] = 0;
        }
    }

    std::array<std::uint64_t, visible> output_rows(const State& state) const {
        std::array<std::uint64_t, visible> result{};
        for (unsigned row = 0; row < visible; ++row) {
            result[row] = (std::uint64_t{1} << row) |
                          (std::uint64_t{state.x[row]} << visible);
        }
        return result;
    }

    std::array<std::uint64_t, visible> top_rows(const State& state) const {
        const auto o = output_rows(state);
        std::array<std::uint64_t, visible> result{};
        for (unsigned row = 0; row < visible; ++row) {
            for (std::uint32_t sources = a_[row]; sources; sources &= sources - 1) {
                result[row] ^= o[std::countr_zero(sources)];
            }
            for (std::uint16_t selected = state.x[row]; selected; selected &= selected - 1) {
                result[row] ^= state.d[std::countr_zero(selected)];
            }
            result[row] &= ((std::uint64_t{1} << bits_) - 1);
        }
        return result;
    }

    SparseScore score(const State& state) const {
        SparseScore result;
        const auto top = top_rows(state);
        for (const auto row : top) {
            const int weight = std::popcount(row);
            account(result, weight);
            result.finals += weight >= 2;
            result.weight_five += weight == 5;
        }
        for (unsigned index = 0; index < hidden_; ++index) {
            const int weight = std::popcount(state.d[index]);
            account(result, weight);
            result.finals += weight >= 2;
            result.weight_five += weight == 5;
        }
        const auto output = output_rows(state);
        for (const auto row : output) {
            const int weight = std::popcount(row);
            account(result, weight);
            result.finals += weight >= 2;
            result.weight_five += weight == 5;
        }
        // This hot-path proxy counts rows rather than deduplicating equal
        // targets.  Exact target-class and sharing accounting is deferred to
        // the certificate pass for any promising printed state.
        // Optimistic: every <=4 parity is one XOR result and every XOR5 is
        // only two Switches plus a NOT.  Pair/XNOR intermediates are omitted,
        // so passing this bound is necessary, never sufficient.
        result.optimistic_logic_gate =
            3 * (result.finals - result.weight_five) + 5 * result.weight_five;
        const int logic_budget = 232 - 5 * static_cast<int>(hidden_);
        result.budget_defect = std::max(0, result.optimistic_logic_gate - logic_budget);
        return result;
    }

    int greedy_xors(const State& state) const {
        std::set<std::uint64_t> targets;
        const auto o = output_rows(state);
        const auto top = top_rows(state);
        for (const auto row : o) {
            if (std::popcount(row) >= 2) targets.insert(row);
        }
        for (const auto row : top) {
            if (std::popcount(row) >= 2) targets.insert(row);
        }
        for (unsigned index = 0; index < hidden_; ++index) {
            if (std::popcount(state.d[index]) >= 2) targets.insert(state.d[index]);
        }

        std::unordered_set<std::uint64_t> pairs;
        for (const auto row : targets) {
            if (std::popcount(row) == 2) pairs.insert(row);
        }

        std::vector<std::uint64_t> pending;
        for (const auto row : targets) {
            if (std::popcount(row) >= 3) pending.push_back(row);
        }
        while (!pending.empty()) {
            int best_index = -1;
            std::vector<std::uint64_t> best_add;
            int best_added = std::numeric_limits<int>::max();
            int best_gain = -1;
            for (unsigned index = 0; index < pending.size(); ++index) {
                const auto options = partitions(pending[index]);
                for (const auto& option : options) {
                    std::vector<std::uint64_t> added;
                    for (const auto pair : option) {
                        if (!pairs.contains(pair)) added.push_back(pair);
                    }
                    int gain = 0;
                    for (const auto other : pending) {
                        for (const auto& other_option : partitions(other)) {
                            bool covered = true;
                            for (const auto pair : other_option) {
                                covered &= pairs.contains(pair) ||
                                           std::find(added.begin(), added.end(), pair) != added.end();
                            }
                            if (covered) {
                                ++gain;
                                break;
                            }
                        }
                    }
                    if (static_cast<int>(added.size()) < best_added ||
                        (static_cast<int>(added.size()) == best_added && gain > best_gain)) {
                        best_index = static_cast<int>(index);
                        best_add = std::move(added);
                        best_added = static_cast<int>(best_add.size());
                        best_gain = gain;
                    }
                }
            }
            for (const auto pair : best_add) pairs.insert(pair);
            pending.erase(
                std::remove_if(pending.begin(), pending.end(), [&](auto row) {
                    for (const auto& option : partitions(row)) {
                        if (std::all_of(option.begin(), option.end(),
                                        [&](auto pair) { return pairs.contains(pair); })) {
                            return true;
                        }
                    }
                    return false;
                }),
                pending.end());
            if (best_index < 0) throw std::runtime_error("pair-cover stalled");
        }
        int pair_targets = 0;
        for (const auto row : targets) pair_targets += std::popcount(row) == 2;
        return static_cast<int>(targets.size() + pairs.size()) - pair_targets;
    }

    bool coordinate_x(State& state, unsigned index) const {
        const auto before = score(state);
        SparseScore best = before;
        std::uint16_t best_value = state.x[index];
        std::uint64_t ties = 1;
        for (const auto candidate : x_domain_) {
            if (candidate == state.x[index]) continue;
            State proposal = state;
            proposal.x[index] = candidate;
            const auto value = score(proposal);
            if (value < best) {
                best = value;
                best_value = candidate;
                ties = 1;
            } else if (value == best) {
                ++ties;
                if ((generator_() % ties) == 0) best_value = candidate;
            }
        }
        if (best < before || (best == before && best_value != state.x[index] && generator_() % 4 == 0)) {
            state.x[index] = best_value;
            return true;
        }
        return false;
    }

    bool coordinate_d(State& state, unsigned index) const {
        const auto before = score(state);
        SparseScore best = before;
        std::uint64_t best_value = state.d[index];
        std::uint64_t ties = 1;
        for (const auto candidate : d_domain_) {
            if (candidate == state.d[index]) continue;
            State proposal = state;
            proposal.d[index] = candidate;
            const auto value = score(proposal);
            if (value < best) {
                best = value;
                best_value = candidate;
                ties = 1;
            } else if (value == best) {
                ++ties;
                if ((generator_() % ties) == 0) best_value = candidate;
            }
        }
        if (best < before || (best == before && best_value != state.d[index] && generator_() % 8 == 0)) {
            state.d[index] = best_value;
            return true;
        }
        return false;
    }

    void descend(State& state, unsigned sweeps) const {
        std::vector<unsigned> x_order(visible);
        std::vector<unsigned> d_order(hidden_);
        std::iota(x_order.begin(), x_order.end(), 0);
        std::iota(d_order.begin(), d_order.end(), 0);
        for (unsigned sweep = 0; sweep < sweeps; ++sweep) {
            bool changed = false;
            std::shuffle(x_order.begin(), x_order.end(), generator_);
            for (const auto index : x_order) changed |= coordinate_x(state, index);
            std::shuffle(d_order.begin(), d_order.end(), generator_);
            for (const auto index : d_order) changed |= coordinate_d(state, index);
            if (!changed) break;
        }
    }

    void kick(State& state, unsigned strength) const {
        for (unsigned move = 0; move < strength; ++move) {
            constexpr std::array<unsigned, 5> widths{8, 24, 64, 128, 512};
            const unsigned width = widths[generator_() % widths.size()];
            if ((generator_() % 100) < 55) {
                guided_x(state, generator_() % visible, width);
            } else {
                const unsigned index = generator_() % hidden_;
                guided_d(state, index, width);
            }
        }
    }

    void print(const State& state, const SparseScore& sparse, const char* label) const {
        const int xor_count = sparse.unsupported == 0 && sparse.weight_five == 0
            ? greedy_xors(state) : -1;
        const int xor_limit = (232 - 5 * static_cast<int>(hidden_)) / 3;
        std::cout << label << " hidden=" << hidden_
                  << " unsupported=" << sparse.unsupported
                  << " max=" << sparse.maximum
                  << " w5=" << sparse.weight_five
                  << " finals=" << sparse.finals
                  << " optimistic_logic_gate=" << sparse.optimistic_logic_gate
                  << " budget_defect=" << sparse.budget_defect
                  << " total=" << sparse.total_weight
                  << " greedy_xor=" << xor_count
                  << " winning_xor_limit=" << xor_limit
                  << " X=";
        for (unsigned index = 0; index < visible; ++index) {
            if (index) std::cout << ',';
            std::cout << std::hex << std::setw(3) << std::setfill('0') << state.x[index];
        }
        std::cout << " D=";
        for (unsigned index = 0; index < hidden_; ++index) {
            if (index) std::cout << ',';
            std::cout << std::hex << std::setw(11) << std::setfill('0') << state.d[index];
        }
        std::cout << std::dec << '\n';
    }

private:
    template <typename Value>
    Value choose_near_best(
        std::vector<std::pair<SparseScore, Value>>& candidates,
        unsigned width
    ) const {
        const auto count = std::min<std::size_t>(width, candidates.size());
        std::partial_sort(
            candidates.begin(), candidates.begin() + count, candidates.end(),
            [](const auto& left, const auto& right) {
                return left.first < right.first;
            });
        return candidates[generator_() % count].second;
    }

    void guided_x(State& state, unsigned index, unsigned width) const {
        std::vector<std::pair<SparseScore, std::uint16_t>> candidates;
        candidates.reserve(x_domain_.size() - 1);
        for (const auto value : x_domain_) {
            if (value == state.x[index]) continue;
            State proposal = state;
            proposal.x[index] = value;
            candidates.emplace_back(score(proposal), value);
        }
        state.x[index] = choose_near_best(candidates, width);
    }

    void guided_d(State& state, unsigned index, unsigned width) const {
        std::vector<std::pair<SparseScore, std::uint64_t>> candidates;
        candidates.reserve(d_domain_.size() - 1);
        for (const auto value : d_domain_) {
            if (value == state.d[index]) continue;
            State proposal = state;
            proposal.d[index] = value;
            candidates.emplace_back(score(proposal), value);
        }
        state.d[index] = choose_near_best(candidates, width);
    }

    std::vector<std::vector<std::uint64_t>> partitions(std::uint64_t row) const {
        std::vector<unsigned> set;
        for (auto value = row; value; value &= value - 1) set.push_back(std::countr_zero(value));
        std::vector<std::vector<std::uint64_t>> result;
        if (set.size() == 3) {
            for (unsigned lone = 0; lone < 3; ++lone) {
                std::uint64_t pair = 0;
                for (unsigned index = 0; index < 3; ++index) {
                    if (index != lone) pair |= std::uint64_t{1} << set[index];
                }
                result.push_back({pair});
            }
        } else if (set.size() == 4) {
            for (unsigned mate = 1; mate < 4; ++mate) {
                const auto first = (std::uint64_t{1} << set[0]) |
                                   (std::uint64_t{1} << set[mate]);
                result.push_back({first, row ^ first});
            }
        }
        return result;
    }

    void build_domains() {
        for (unsigned value = 0; value < (1u << hidden_); ++value) {
            if (std::popcount(value) <= 3) x_domain_.push_back(static_cast<std::uint16_t>(value));
        }
        const std::uint64_t limit = std::uint64_t{1} << bits_;
        for (unsigned a = 0; a < bits_; ++a) {
            d_domain_.push_back(std::uint64_t{1} << a);
        }
        for (unsigned a = 0; a < bits_; ++a) {
            for (unsigned b = a + 1; b < bits_; ++b) {
                d_domain_.push_back((std::uint64_t{1} << a) | (std::uint64_t{1} << b));
            }
        }
        for (unsigned a = 0; a < bits_; ++a) {
            for (unsigned b = a + 1; b < bits_; ++b) {
                for (unsigned c = b + 1; c < bits_; ++c) {
                    d_domain_.push_back((std::uint64_t{1} << a) |
                                        (std::uint64_t{1} << b) |
                                        (std::uint64_t{1} << c));
                }
            }
        }
        for (unsigned a = 0; a < bits_; ++a) {
            for (unsigned b = a + 1; b < bits_; ++b) {
                for (unsigned c = b + 1; c < bits_; ++c) {
                    for (unsigned d = c + 1; d < bits_; ++d) {
                        const auto value = (std::uint64_t{1} << a) |
                                           (std::uint64_t{1} << b) |
                                           (std::uint64_t{1} << c) |
                                           (std::uint64_t{1} << d);
                        if (value < limit) d_domain_.push_back(value);
                    }
                }
            }
        }
    }

    void build_column_users() {
        for (unsigned column = 0; column < visible; ++column) {
            for (unsigned row = 0; row < visible; ++row) {
                if ((a_[row] >> column) & 1u) column_users_[column].push_back(row);
            }
        }
    }

    unsigned hidden_;
    unsigned bits_;
    mutable std::mt19937_64 generator_;
    std::array<std::uint32_t, visible> a_{};
    std::array<std::vector<unsigned>, visible> column_users_{};
    std::vector<std::uint16_t> x_domain_;
    std::vector<std::uint64_t> d_domain_;
};

}  // namespace

int main(int argc, char** argv) {
    unsigned hidden = 10;
    unsigned basins = 20;
    unsigned sweeps = 3;
    std::uint64_t seed = 0x42a11d17ULL;
    if (argc > 1) hidden = static_cast<unsigned>(std::stoul(argv[1]));
    if (argc > 2) basins = static_cast<unsigned>(std::stoul(argv[2]));
    if (argc > 3) sweeps = static_cast<unsigned>(std::stoul(argv[3]));
    if (argc > 4) seed = std::stoull(argv[4]);

    Search search(hidden, seed);
    State best_state;
    search.set_known_start(best_state);
    auto best_score = search.score(best_state);
    search.print(best_state, best_score, "initial");

    State incumbent = best_state;
    auto incumbent_score = best_score;
    for (unsigned basin = 0; basin < basins; ++basin) {
        State current = incumbent;
        if (basin != 0 && basin % 40 != 39) {
            const unsigned strength = 2 + basin % 13;
            search.kick(current, strength);
        } else if (basin % 40 == 39) {
            search.random_start(current);
        }
        search.descend(current, sweeps);
        const auto current_score = search.score(current);
        if (current_score < best_score) {
            best_state = current;
            best_score = current_score;
            search.print(best_state, best_score, "best");
        }

        const double old_energy = 100000.0 * incumbent_score.unsupported +
                                  10000.0 * incumbent_score.budget_defect +
                                  100.0 * incumbent_score.optimistic_logic_gate +
                                  20.0 * incumbent_score.weight_five +
                                  incumbent_score.total_weight;
        const double new_energy = 100000.0 * current_score.unsupported +
                                  10000.0 * current_score.budget_defect +
                                  100.0 * current_score.optimistic_logic_gate +
                                  20.0 * current_score.weight_five +
                                  current_score.total_weight;
        if (new_energy <= old_energy) {
            incumbent = current;
            incumbent_score = current_score;
        } else if (basin % 5 == 4) {
            incumbent = best_state;
            incumbent_score = best_score;
        }
    }
    search.print(best_state, best_score, "final");
    return best_score.unsupported == 0 && best_score.budget_defect == 0 ? 0 : 2;
}
