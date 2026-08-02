#include <algorithm>
#include <array>
#include <bit>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <limits>
#include <random>
#include <set>
#include <sstream>
#include <string>
#include <tuple>
#include <unordered_set>
#include <vector>

namespace {

constexpr unsigned visible = 32;
constexpr unsigned hidden = 10;
constexpr unsigned state_bits = visible + hidden;
constexpr std::uint64_t state_mask = (std::uint64_t{1} << state_bits) - 1;
int excess_proxy_weight = 10;

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
    std::array<std::uint64_t, hidden> d{};
};

struct Score {
    int unsupported = 0;
    int excess4 = 0;
    int raw_excess4 = 0;
    int maximum = 0;
    int base_finals = 0;
    int active_hidden = 0;
    int optimistic_total_gate = 1000000;
    int switch_proxy_total = 1000000;
    int total_weight = 0;
    int budget_defect = 1000000;

    auto key() const {
        // optimistic_total_gate is a hard lower bound.  A state already above
        // 430 must never hide a lower-proxy state that still has a chance.
        return std::tie(unsupported, budget_defect, switch_proxy_total,
                        optimistic_total_gate, excess4, active_hidden,
                        base_finals, maximum, total_weight);
    }
};

bool operator<(const Score& left, const Score& right) {
    return left.key() < right.key();
}

std::array<std::uint64_t, visible> output_rows(const State& state) {
    std::array<std::uint64_t, visible> result{};
    for (unsigned i = 0; i < visible; ++i) {
        result[i] = (std::uint64_t{1} << i) |
                    (std::uint64_t{state.x[i]} << visible);
    }
    return result;
}

std::array<std::uint64_t, visible> top_rows(
    const State& state,
    const std::array<std::uint32_t, visible>& a
) {
    const auto o = output_rows(state);
    std::array<std::uint64_t, visible> result{};
    for (unsigned row = 0; row < visible; ++row) {
        std::uint32_t sources = a[row];
        while (sources) {
            const auto low = sources & (0u - sources);
            result[row] ^= o[std::countr_zero(low)];
            sources ^= low;
        }
        std::uint16_t correction = state.x[row];
        while (correction) {
            const auto low = static_cast<std::uint16_t>(
                correction & static_cast<std::uint16_t>(0u - correction)
            );
            result[row] ^= state.d[std::countr_zero(low)];
            correction ^= low;
        }
        result[row] &= state_mask;
    }
    return result;
}

std::uint16_t essential_hidden_mask(const State& state) {
    std::uint16_t reachable = 0;
    bool changed = true;
    while (changed) {
        changed = false;
        for (unsigned j = 0; j < hidden; ++j) {
            if ((reachable >> j) & 1u) {
                continue;
            }
            const auto visible_drivers = static_cast<std::uint32_t>(state.d[j]);
            const auto hidden_drivers = static_cast<std::uint16_t>(state.d[j] >> visible);
            if (visible_drivers != 0 || (hidden_drivers & reachable) != 0) {
                reachable |= static_cast<std::uint16_t>(1u << j);
                changed = true;
            }
        }
    }

    std::uint16_t observable = 0;
    for (const auto row : state.x) {
        observable |= row;
    }
    changed = true;
    while (changed) {
        changed = false;
        auto expanded = observable;
        for (unsigned j = 0; j < hidden; ++j) {
            if ((observable >> j) & 1u) {
                expanded |= static_cast<std::uint16_t>(state.d[j] >> visible);
            }
        }
        if (expanded != observable) {
            observable = expanded;
            changed = true;
        }
    }
    return static_cast<std::uint16_t>(reachable & observable);
}

std::uint16_t remap_hidden_bits(std::uint16_t value, std::uint16_t keep) {
    std::uint16_t result = 0;
    unsigned target = 0;
    for (unsigned source = 0; source < hidden; ++source) {
        if ((keep >> source) & 1u) {
            if ((value >> source) & 1u) {
                result |= static_cast<std::uint16_t>(1u << target);
            }
            ++target;
        }
    }
    return result;
}

// Remove hidden coordinates that are zero from the strict-zero load state or
// cannot influence O.  Iterate because projecting one side can expose another
// dead coordinate.  This is a behavior-preserving state-space projection.
int canonicalize(State& state) {
    for (unsigned pass = 0; pass < hidden; ++pass) {
        const auto keep = essential_hidden_mask(state);
        const int count = std::popcount(keep);
        const auto packed = static_cast<std::uint16_t>(
            count == 0 ? 0u : ((1u << count) - 1u)
        );
        if (keep == packed) {
            bool clean = true;
            for (const auto row : state.x) {
                clean &= (row & static_cast<std::uint16_t>(~packed)) == 0;
            }
            for (unsigned j = 0; j < static_cast<unsigned>(count); ++j) {
                const auto columns = static_cast<std::uint16_t>(state.d[j] >> visible);
                clean &= (columns & static_cast<std::uint16_t>(~packed)) == 0;
            }
            for (unsigned j = static_cast<unsigned>(count); j < hidden; ++j) {
                clean &= state.d[j] == 0;
            }
            if (clean) {
                return count;
            }
        }

        State compact;
        for (unsigned i = 0; i < visible; ++i) {
            compact.x[i] = remap_hidden_bits(state.x[i], keep);
        }
        unsigned target = 0;
        for (unsigned source = 0; source < hidden; ++source) {
            if (!((keep >> source) & 1u)) {
                continue;
            }
            const auto low = static_cast<std::uint32_t>(state.d[source]);
            const auto high = remap_hidden_bits(
                static_cast<std::uint16_t>(state.d[source] >> visible), keep
            );
            compact.d[target++] = static_cast<std::uint64_t>(low) |
                                  (static_cast<std::uint64_t>(high) << visible);
        }
        state = compact;
    }
    return std::popcount(essential_hidden_mask(state));
}

std::vector<std::vector<std::vector<std::uint64_t>>> pair_requirements(
    const std::vector<std::uint64_t>& targets
) {
    std::vector<std::vector<std::vector<std::uint64_t>>> requirements;
    for (const auto row : targets) {
        const int weight = std::popcount(row);
        if (weight < 3) {
            continue;
        }
        std::vector<unsigned> bits;
        for (std::uint64_t value = row; value; value &= value - 1) {
            bits.push_back(std::countr_zero(value));
        }
        std::vector<std::vector<std::uint64_t>> options;
        if (weight == 3) {
            for (unsigned skip = 0; skip < 3; ++skip) {
                std::uint64_t pair = 0;
                for (unsigned i = 0; i < 3; ++i) {
                    if (i != skip) {
                        pair |= std::uint64_t{1} << bits[i];
                    }
                }
                options.push_back({pair});
            }
        } else if (weight == 4) {
            for (unsigned mate = 1; mate < 4; ++mate) {
                const auto first = (std::uint64_t{1} << bits[0]) |
                                   (std::uint64_t{1} << bits[mate]);
                std::uint64_t second = row ^ first;
                options.push_back({first, second});
            }
        }
        if (!options.empty()) {
            requirements.push_back(std::move(options));
        }
    }
    return requirements;
}

[[maybe_unused]] int greedy_xor_count(const std::vector<std::uint64_t>& raw_targets) {
    std::set<std::uint64_t> distinct;
    for (const auto row : raw_targets) {
        if (std::popcount(row) >= 2) {
            distinct.insert(row);
        }
    }
    std::unordered_set<std::uint64_t> available;
    for (const auto row : distinct) {
        if (std::popcount(row) == 2) {
            available.insert(row);
        }
    }
    auto requirements = pair_requirements(
        std::vector<std::uint64_t>(distinct.begin(), distinct.end())
    );
    std::vector<bool> done(requirements.size());
    std::size_t remaining = requirements.size();
    while (remaining) {
        int chosen_requirement = -1;
        int chosen_option = -1;
        int chosen_new = std::numeric_limits<int>::max();
        int chosen_gain = -1;
        for (unsigned r = 0; r < requirements.size(); ++r) {
            if (done[r]) {
                continue;
            }
            for (unsigned option = 0; option < requirements[r].size(); ++option) {
                int added = 0;
                for (const auto pair : requirements[r][option]) {
                    added += !available.contains(pair);
                }
                int gain = 0;
                for (unsigned other = 0; other < requirements.size(); ++other) {
                    if (done[other]) {
                        continue;
                    }
                    for (const auto& other_option : requirements[other]) {
                        bool covered = true;
                        for (const auto pair : other_option) {
                            covered &= available.contains(pair) ||
                                       std::find(
                                           requirements[r][option].begin(),
                                           requirements[r][option].end(),
                                           pair
                                       ) != requirements[r][option].end();
                        }
                        if (covered) {
                            ++gain;
                            break;
                        }
                    }
                }
                if (std::tie(added, gain) <
                    std::tie(chosen_new, chosen_gain)) {
                    // The gain comparison is corrected below for equal cost.
                }
                if (added < chosen_new ||
                    (added == chosen_new && gain > chosen_gain)) {
                    chosen_requirement = static_cast<int>(r);
                    chosen_option = static_cast<int>(option);
                    chosen_new = added;
                    chosen_gain = gain;
                }
            }
        }
        for (const auto pair : requirements[chosen_requirement][chosen_option]) {
            available.insert(pair);
        }
        for (unsigned r = 0; r < requirements.size(); ++r) {
            if (done[r]) {
                continue;
            }
            for (const auto& option : requirements[r]) {
                if (std::all_of(option.begin(), option.end(), [&](auto pair) {
                        return available.contains(pair);
                    })) {
                    done[r] = true;
                    --remaining;
                    break;
                }
            }
        }
    }
    return static_cast<int>(distinct.size() + available.size() -
                            std::count_if(distinct.begin(), distinct.end(), [](auto row) {
                                return std::popcount(row) == 2;
                            }));
}

Score evaluate(
    const State& state,
    const std::array<std::uint32_t, visible>& a
) {
    Score score;
    std::vector<std::uint64_t> targets;
    const auto o = output_rows(state);
    const auto top = top_rows(state, a);
    targets.insert(targets.end(), o.begin(), o.end());
    targets.insert(targets.end(), top.begin(), top.end());
    targets.insert(targets.end(), state.d.begin(), state.d.end());
    std::set<std::uint64_t> finals;
    for (const auto row : targets) {
        const int weight = std::popcount(row);
        score.raw_excess4 += std::max(0, weight - 4);
        if (weight >= 2) {
            finals.insert(row);
        }
    }
    for (const auto row : finals) {
        const int weight = std::popcount(row);
        score.unsupported += std::max(0, weight - 9);
        score.excess4 += std::max(0, weight - 4);
        score.maximum = std::max(score.maximum, weight);
        score.total_weight += weight;
    }
    score.base_finals = static_cast<int>(finals.size());
    score.active_hidden = std::popcount(essential_hidden_mask(state));
    // 32 visible state bits, phase ORs and ready control cost 198 gates.
    // Each active hidden state costs another five.  Three gates per distinct
    // target is an optimistic lower bound that omits every pair/triple node.
    score.optimistic_total_gate =
        198 + 5 * score.active_hidden + 3 * score.base_finals;
    // Each unit above support four forces additional shallow group structure.
    // Ten gates per unit is empirical guidance only; exact PySAT cover follows
    // for every promising printed state.
    score.switch_proxy_total = score.optimistic_total_gate +
                               excess_proxy_weight * score.excess4;
    score.budget_defect = std::max(0, score.optimistic_total_gate - 430);
    return score;
}

double energy(const Score& score) {
    return 100000000.0 * score.unsupported +
           1000000.0 * score.budget_defect +
           1000.0 * score.switch_proxy_total + score.total_weight;
}

std::vector<std::uint16_t> masks() {
    std::vector<std::uint16_t> result;
    for (unsigned value = 0; value < (1u << hidden); ++value) {
        if (std::popcount(value) <= 3) {
            result.push_back(static_cast<std::uint16_t>(value));
        }
    }
    return result;
}

std::uint64_t random_sparse_row(std::mt19937_64& generator) {
    std::uint64_t row = 0;
    const unsigned weight = static_cast<unsigned>(generator() % 5);
    while (std::popcount(row) < static_cast<int>(weight)) {
        row |= std::uint64_t{1} << (generator() % state_bits);
    }
    return row;
}

void initialize(
    State& state,
    unsigned restart,
    std::mt19937_64& generator,
    const std::array<std::uint32_t, visible>& a,
    const std::vector<std::uint16_t>& candidate_masks
) {
    constexpr std::array<std::uint16_t, visible> resume_x{
        0x010, 0x022, 0x040, 0x004, 0x008, 0x090, 0x0e0, 0x040,
        0x100, 0x200, 0x080, 0x044, 0x101, 0x100, 0x200, 0x004,
        0x008, 0x011, 0x022, 0x040, 0x004, 0x108, 0x210, 0x020,
        0x040, 0x100, 0x300, 0x280, 0x000, 0x000, 0x100, 0x000,
    };
    constexpr std::array<std::uint64_t, hidden> resume_d{
        0x20040020001, 0x20000044002, 0x00000110008, 0x00100220010,
        0x02200040020, 0x08000880040, 0x00401100080, 0x02000800400,
        0x20084002000, 0x08008404000,
    };
    constexpr std::array<std::uint16_t, visible> low_base_x{
        0x000, 0x000, 0x001, 0x010, 0x084, 0x002, 0x001, 0x001,
        0x084, 0x200, 0x000, 0x001, 0x000, 0x204, 0x000, 0x000,
        0x000, 0x080, 0x206, 0x001, 0x010, 0x004, 0x006, 0x000,
        0x001, 0x010, 0x004, 0x000, 0x000, 0x000, 0x284, 0x000,
    };
    constexpr std::array<std::uint64_t, hidden> low_base_d{
        0x00001100080, 0x20004840000, 0x20204400000, 0x00020000000,
        0x01002200100, 0x00000000010, 0x00000010000, 0x00200022000,
        0x04800000022, 0x20400404000,
    };
    constexpr std::array<std::uint32_t, hidden> frontier_r{
        0x00002001, 0x00004002, 0x00010008, 0x00020010, 0x00040020,
        0x00080040, 0x00100080, 0x00800400, 0x04002000, 0x08004000,
    };
    // Hidden transition rows D=R*[I|X] from nearest_invalid_certificate.json.
    // Keeping only R drops the high ten columns and destroys that start.
    constexpr std::array<std::uint64_t, hidden> nearest_d{
        0x12000042000, 0x00800200100, 0x00800010008, 0x01100020010,
        0x10840000010, 0x04000080040, 0x00600100080, 0x00000800400,
        0x30004002000, 0x28008004000,
    };
    constexpr std::array<std::uint16_t, visible> nearest_x{
        0x201, 0x020, 0x040, 0x000, 0x008, 0x080, 0x020, 0x040,
        0x100, 0x280, 0x000, 0x000, 0x110, 0x100, 0x200, 0x004,
        0x008, 0x019, 0x020, 0x060, 0x046, 0x108, 0x280, 0x000,
        0x040, 0x100, 0x200, 0x080, 0x000, 0x000, 0x100, 0x200,
    };

    if (restart == 0) {
        state.x = resume_x;
        state.d = resume_d;
        canonicalize(state);
        return;
    }
    if (restart == 1) {
        state.x = low_base_x;
        state.d = low_base_d;
        canonicalize(state);
        return;
    }
    if (restart == 2) {
        state.x = nearest_x;
        for (unsigned j = 0; j < hidden; ++j) {
            state.d[j] = nearest_d[j];
        }
        canonicalize(state);
        return;
    }
    for (unsigned j = 0; j < hidden; ++j) {
        if (restart < 6) {
            state.d[j] = frontier_r[j];
        } else {
            state.d[j] = random_sparse_row(generator);
        }
    }
    // Independently minimize each main 32-bit residual before considering the
    // coupled auxiliary columns.
    for (unsigned i = 0; i < visible; ++i) {
        int best = std::numeric_limits<int>::max();
        std::vector<std::uint16_t> choices;
        for (const auto mask : candidate_masks) {
            std::uint32_t residual = a[i];
            for (unsigned j = 0; j < hidden; ++j) {
                if ((mask >> j) & 1u) {
                    residual ^= static_cast<std::uint32_t>(state.d[j]);
                }
            }
            const int weight = std::popcount(residual);
            if (weight < best) {
                best = weight;
                choices.clear();
            }
            if (weight == best) {
                choices.push_back(mask);
            }
        }
        state.x[i] = choices[generator() % choices.size()];
    }
    canonicalize(state);
}

Score polish(
    State& state,
    const std::array<std::uint32_t, visible>& a,
    const std::vector<std::uint16_t>& candidate_masks
) {
    canonicalize(state);
    auto current = evaluate(state, a);
    for (unsigned pass = 0; pass < 12; ++pass) {
        bool changed = false;
        for (unsigned i = 0; i < visible; ++i) {
            auto best_state = state;
            auto best_score = current;
            for (const auto mask : candidate_masks) {
                State proposal = state;
                proposal.x[i] = mask;
                canonicalize(proposal);
                const auto score = evaluate(proposal, a);
                if (score < best_score) {
                    best_state = proposal;
                    best_score = score;
                }
            }
            if (best_score < current) {
                state = best_state;
                current = best_score;
                changed = true;
            }
        }
        for (unsigned j = 0; j < hidden; ++j) {
            auto best_state = state;
            auto best_score = current;
            const auto original = state.d[j];
            std::vector<unsigned> present;
            std::vector<unsigned> absent;
            for (unsigned bit = 0; bit < state_bits; ++bit) {
                (((original >> bit) & 1u) ? present : absent).push_back(bit);
            }
            auto consider = [&](std::uint64_t row) {
                if (std::popcount(row) > 4) {
                    return;
                }
                State proposal = state;
                proposal.d[j] = row;
                canonicalize(proposal);
                const auto score = evaluate(proposal, a);
                if (score < best_score) {
                    best_state = proposal;
                    best_score = score;
                }
            };
            for (const auto bit : present) {
                consider(original ^ (std::uint64_t{1} << bit));
            }
            if (present.size() < 4) {
                for (const auto bit : absent) {
                    consider(original | (std::uint64_t{1} << bit));
                }
            }
            for (const auto remove : present) {
                for (const auto add : absent) {
                    consider(original ^ (std::uint64_t{1} << remove) ^
                             (std::uint64_t{1} << add));
                }
            }
            if (best_score < current) {
                state = best_state;
                current = best_score;
                changed = true;
            }
        }
        if (!changed) {
            break;
        }
    }
    return current;
}

void basis_shear(State& state, unsigned left, unsigned right) {
    const State original = state;
    auto rows = original.d;
    rows[left] ^= original.d[right];
    for (unsigned j = 0; j < hidden; ++j) {
        auto low = static_cast<std::uint32_t>(rows[j]);
        auto high = static_cast<std::uint16_t>(rows[j] >> visible);
        if ((high >> left) & 1u) {
            high ^= static_cast<std::uint16_t>(1u << right);
        }
        state.d[j] = static_cast<std::uint64_t>(low) |
                     (static_cast<std::uint64_t>(high) << visible);
    }
    for (unsigned i = 0; i < visible; ++i) {
        state.x[i] = original.x[i];
        if ((original.x[i] >> left) & 1u) {
            state.x[i] ^= static_cast<std::uint16_t>(1u << right);
        }
    }
}

void activate_hidden(State& state, std::mt19937_64& generator) {
    const unsigned active = std::popcount(essential_hidden_mask(state));
    if (active >= hidden) {
        return;
    }
    const unsigned index = active;
    std::uint64_t row = std::uint64_t{1} << (generator() % visible);
    const unsigned extras = generator() % 4;
    for (unsigned n = 0; n < extras; ++n) {
        row |= std::uint64_t{1} << (generator() % (visible + active));
    }
    state.d[index] = row;
    const unsigned users = 1 + generator() % 4;
    for (unsigned n = 0; n < users; ++n) {
        auto& mask = state.x[generator() % visible];
        if (std::popcount(mask) >= 3) {
            const unsigned victim = std::countr_zero(mask);
            mask ^= static_cast<std::uint16_t>(1u << victim);
        }
        mask |= static_cast<std::uint16_t>(1u << index);
    }
}

void mutate(
    State& proposal,
    std::mt19937_64& generator,
    const std::vector<std::uint16_t>& candidate_masks
) {
    canonicalize(proposal);
    const unsigned active = std::popcount(essential_hidden_mask(proposal));
    unsigned kind = static_cast<unsigned>(generator() % 100);
    if (active == 0) {
        kind = 85;
    }

    if (kind < 45) {
        const auto live_mask = static_cast<std::uint16_t>(
            active == 0 ? 0u : ((1u << active) - 1u)
        );
        proposal.x[generator() % visible] = static_cast<std::uint16_t>(
            candidate_masks[generator() % candidate_masks.size()] & live_mask
        );
    } else if (kind < 70) {
        auto& row = proposal.d[generator() % active];
        if ((generator() % 100) < 12) {
            row = random_sparse_row(generator);
        } else {
            const unsigned bit = static_cast<unsigned>(
                generator() % (visible + active)
            );
            if ((row >> bit) & 1u) {
                // Singleton rows must be allowed to become zero, otherwise the
                // annealer can never reduce its active-state count.
                row ^= std::uint64_t{1} << bit;
            } else {
                if (std::popcount(row) == 4) {
                    const unsigned victim = static_cast<unsigned>(
                        generator() % static_cast<unsigned>(std::popcount(row))
                    );
                    unsigned seen = 0;
                    for (std::uint64_t value = row; value; value &= value - 1) {
                        const unsigned set_bit = std::countr_zero(value);
                        if (seen++ == victim) {
                            row ^= std::uint64_t{1} << set_bit;
                            break;
                        }
                    }
                }
                row |= std::uint64_t{1} << bit;
            }
        }
    } else if (kind < 80) {
        const unsigned victim = static_cast<unsigned>(generator() % active);
        proposal.d[victim] = 0;
        for (auto& mask : proposal.x) {
            mask &= static_cast<std::uint16_t>(~(1u << victim));
        }
    } else if (kind < 92) {
        activate_hidden(proposal, generator);
    } else if (active >= 2) {
        unsigned left = static_cast<unsigned>(generator() % active);
        unsigned right = static_cast<unsigned>(generator() % active);
        while (right == left) {
            right = static_cast<unsigned>(generator() % active);
        }
        basis_shear(proposal, left, right);
    }
    canonicalize(proposal);
}

bool verify_sequences(
    const State& state,
    const std::array<std::uint32_t, visible>& a
) {
    const auto top = top_rows(state, a);
    const auto output = output_rows(state);
    std::array<std::uint64_t, state_bits> transition{};
    for (unsigned row = 0; row < visible; ++row) {
        transition[row] = top[row];
    }
    for (unsigned row = 0; row < hidden; ++row) {
        transition[visible + row] = state.d[row];
    }

    for (unsigned seed = 0; seed < 256; ++seed) {
        std::uint64_t encoded = seed;
        std::uint32_t expected = seed;
        for (unsigned tick = 1; tick <= 65; ++tick) {
            std::uint64_t next = 0;
            for (unsigned row = 0; row < state_bits; ++row) {
                if (std::popcount(encoded & transition[row]) & 1) {
                    next |= std::uint64_t{1} << row;
                }
            }
            encoded = next;
            expected = xorshift32(expected);
            std::uint32_t observed = 0;
            for (unsigned row = 0; row < visible; ++row) {
                if (std::popcount(encoded & output[row]) & 1) {
                    observed |= std::uint32_t{1} << row;
                }
            }
            if (observed != expected) {
                return false;
            }
        }
    }
    return true;
}

void print_state(
    const State& state,
    const Score& score,
    const char* label,
    std::uint64_t seed,
    unsigned restart,
    std::uint64_t iteration,
    const std::array<std::uint32_t, visible>& a
) {
    std::cout << "label=" << label
              << " seed=" << seed
              << " excess_weight=" << excess_proxy_weight
              << " restart=" << restart
              << " iteration=" << iteration
              << " verified=" << (verify_sequences(state, a) ? "256x65" : "FAIL")
              << " unsupported=" << score.unsupported
              << " excess4=" << score.excess4
              << " raw_excess4=" << score.raw_excess4
              << " max=" << score.maximum
              << " base=" << score.base_finals
              << " active_hidden=" << score.active_hidden
              << " optimistic_total_gate=" << score.optimistic_total_gate
              << " switch_proxy_total=" << score.switch_proxy_total
              << " defect=" << score.budget_defect
              << " total=" << score.total_weight << " X=";
    for (unsigned i = 0; i < visible; ++i) {
        if (i) {
            std::cout << ',';
        }
        std::cout << std::hex << std::setw(3) << std::setfill('0') << state.x[i];
    }
    std::cout << " D=";
    for (unsigned j = 0; j < hidden; ++j) {
        if (j) {
            std::cout << ',';
        }
        std::cout << std::hex << std::setw(11) << std::setfill('0') << state.d[j];
    }
    std::cout << std::dec << '\n' << std::flush;
}

}  // namespace

int main(int argc, char** argv) {
    std::uint64_t iterations = 5'000'000;
    unsigned restarts = 16;
    std::uint64_t seed = 0x431'0042u;
    if (argc > 1) {
        iterations = std::stoull(argv[1]);
    }
    if (argc > 2) {
        restarts = static_cast<unsigned>(std::stoul(argv[2]));
    }
    if (argc > 3) {
        seed = std::stoull(argv[3]);
    }
    if (argc > 4) {
        excess_proxy_weight = std::stoi(argv[4]);
        if (excess_proxy_weight < 0 || excess_proxy_weight > 100) {
            throw std::runtime_error("excess weight must be in 0..100");
        }
    }

    const auto a = transition_rows();
    const auto candidate_masks = masks();
    std::mt19937_64 generator(seed);
    std::uniform_real_distribution<double> unit(0.0, 1.0);
    State global_state;
    Score global_score;
    global_score.unsupported = std::numeric_limits<int>::max();
    std::array<State, hidden + 1> active_best_state{};
    std::array<Score, hidden + 1> active_best_score{};
    std::array<std::vector<Score>, hidden + 1> pareto_scores{};
    for (auto& score : active_best_score) {
        score.unsupported = std::numeric_limits<int>::max();
    }

    auto publish = [&](const State& state, const Score& score, const char* label,
                       unsigned restart, std::uint64_t iteration) {
        const auto active = static_cast<unsigned>(score.active_hidden);
        auto weakly_dominates = [](const Score& left, const Score& right) {
            return left.unsupported <= right.unsupported &&
                   left.budget_defect <= right.budget_defect &&
                   left.base_finals <= right.base_finals &&
                   left.excess4 <= right.excess4 &&
                   left.maximum <= right.maximum &&
                   left.total_weight <= right.total_weight;
        };
        const bool dominated = std::any_of(
            pareto_scores[active].begin(), pareto_scores[active].end(),
            [&](const Score& prior) { return weakly_dominates(prior, score); }
        );
        if (!dominated) {
            std::erase_if(pareto_scores[active], [&](const Score& prior) {
                return weakly_dominates(score, prior);
            });
            pareto_scores[active].push_back(score);
            print_state(state, score, "pareto", seed, restart, iteration, a);
        }
        if (score < active_best_score[active]) {
            active_best_state[active] = state;
            active_best_score[active] = score;
            print_state(state, score, label, seed, restart, iteration, a);
        }
        if (score < global_score) {
            global_state = state;
            global_score = score;
            print_state(state, score, "global", seed, restart, iteration, a);
        }
    };

    for (unsigned restart = 0; restart < restarts; ++restart) {
        State current;
        initialize(current, restart, generator, a, candidate_masks);
        auto current_score = polish(current, a, candidate_masks);
        publish(current, current_score, "frontier", restart, 0);
        for (std::uint64_t iteration = 0; iteration < iterations; ++iteration) {
            State proposal = current;
            mutate(proposal, generator, candidate_masks);
            const auto proposal_score = evaluate(proposal, a);
            const double progress = static_cast<double>(iteration) /
                                    static_cast<double>(iterations);
            const double temperature = 10000.0 * (1.0 - progress) + 20.0;
            const double delta = energy(proposal_score) - energy(current_score);
            if (delta <= 0.0 || unit(generator) < std::exp(-delta / temperature)) {
                current = proposal;
                current_score = proposal_score;
            }
            publish(current, current_score, "frontier", restart, iteration + 1);
        }
        current_score = polish(current, a, candidate_masks);
        publish(current, current_score, "polished", restart, iterations);
    }
    if (restarts == 0) {
        std::cerr << "restarts must be positive\n";
        return 2;
    }
    print_state(global_state, global_score, "final", seed, restarts - 1,
                iterations, a);
    // Search completion is not a synthesis certificate.  Exact cover decides
    // whether a printed candidate is a winning implementation.
    return 0;
}
