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
#include <stdexcept>
#include <string>
#include <tuple>
#include <unordered_map>
#include <unordered_set>
#include <vector>

namespace {

constexpr unsigned visible = 32;
constexpr unsigned hidden = 10;
constexpr unsigned state_bits = visible + hidden;
constexpr std::uint64_t state_mask = (std::uint64_t{1} << state_bits) - 1;
constexpr int pair_universe = state_bits * (state_bits - 1) / 2;
constexpr int triple_universe = state_bits * (state_bits - 1) * (state_bits - 2) / 6;
constexpr int group_universe = pair_universe + triple_universe;

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

struct BlockTemplate {
    std::array<std::uint8_t, 3> positions{};
    std::uint8_t size = 0;
};

struct OptionTemplate {
    std::array<BlockTemplate, 3> blocks{};
    std::uint8_t count = 0;
    std::uint8_t final_units = 0;
};

using TemplateTable = std::array<std::vector<OptionTemplate>, 10>;

void enumerate_partitions(
    unsigned weight,
    unsigned position,
    std::array<std::vector<unsigned>, 3>& blocks,
    unsigned block_count,
    std::vector<OptionTemplate>& output
) {
    if (position == weight) {
        if (block_count == 0 || block_count > 3) {
            return;
        }
        OptionTemplate option;
        option.count = static_cast<std::uint8_t>(block_count);
        option.final_units = block_count == 1 ? 0 : (block_count == 2 ? 1 : 4);
        for (unsigned block = 0; block < block_count; ++block) {
            option.blocks[block].size = static_cast<std::uint8_t>(blocks[block].size());
            for (unsigned i = 0; i < blocks[block].size(); ++i) {
                option.blocks[block].positions[i] = static_cast<std::uint8_t>(blocks[block][i]);
            }
        }
        output.push_back(option);
        return;
    }
    for (unsigned block = 0; block < block_count; ++block) {
        if (blocks[block].size() == 3) {
            continue;
        }
        blocks[block].push_back(position);
        enumerate_partitions(weight, position + 1, blocks, block_count, output);
        blocks[block].pop_back();
    }
    if (block_count < 3) {
        blocks[block_count].push_back(position);
        enumerate_partitions(weight, position + 1, blocks, block_count + 1, output);
        blocks[block_count].pop_back();
    }
}

TemplateTable build_templates() {
    TemplateTable table;
    for (unsigned weight = 2; weight <= 9; ++weight) {
        std::array<std::vector<unsigned>, 3> blocks;
        enumerate_partitions(weight, 0, blocks, 0, table[weight]);
    }
    return table;
}

struct ConcreteOption {
    std::array<std::int16_t, 3> groups{-1, -1, -1};
    std::uint8_t group_count = 0;
    std::uint8_t final_units = 0;
};

struct TargetOptions {
    std::uint64_t row = 0;
    std::vector<ConcreteOption> options;
};

struct GreedyCover {
    int logic_units = 1000000;
    int pair_groups = 0;
    int triple_groups = 0;
    int final_xor2 = 0;
    int final_switch3 = 0;
};

int pair_id(unsigned a, unsigned b) {
    if (a > b) {
        std::swap(a, b);
    }
    int id = 0;
    for (unsigned first = 0; first < a; ++first) {
        id += static_cast<int>(state_bits - first - 1);
    }
    return id + static_cast<int>(b - a - 1);
}

int triple_id(unsigned a, unsigned b, unsigned c) {
    std::array<unsigned, 3> values{a, b, c};
    std::sort(values.begin(), values.end());
    a = values[0];
    b = values[1];
    c = values[2];
    int id = 0;
    for (unsigned first = 0; first < a; ++first) {
        const int remaining = static_cast<int>(state_bits - first - 1);
        id += remaining * (remaining - 1) / 2;
    }
    for (unsigned second = a + 1; second < b; ++second) {
        id += static_cast<int>(state_bits - second - 1);
    }
    return pair_universe + id + static_cast<int>(c - b - 1);
}

int group_cost_units(int id) {
    return id < pair_universe ? 1 : 4;
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

struct ProjectedRows {
    std::vector<std::uint64_t> targets;
    std::array<int, hidden> new_hidden{};
    int active_hidden = 0;
};

ProjectedRows project_zero_hidden(
    const State& state,
    const std::array<std::uint32_t, visible>& a
) {
    ProjectedRows projected;
    projected.new_hidden.fill(-1);
    for (unsigned j = 0; j < hidden; ++j) {
        if (state.d[j] != 0) {
            projected.new_hidden[j] = projected.active_hidden++;
        }
    }
    auto project = [&](std::uint64_t row) {
        std::uint64_t result = row & 0xffffffffu;
        for (unsigned j = 0; j < hidden; ++j) {
            if (((row >> (visible + j)) & 1u) && projected.new_hidden[j] >= 0) {
                result |= std::uint64_t{1} << (visible + projected.new_hidden[j]);
            }
        }
        return result;
    };
    const auto o = output_rows(state);
    const auto h = top_rows(state, a);
    projected.targets.reserve(64 + projected.active_hidden);
    for (const auto row : o) {
        projected.targets.push_back(project(row));
    }
    for (const auto row : h) {
        projected.targets.push_back(project(row));
    }
    for (unsigned j = 0; j < hidden; ++j) {
        if (projected.new_hidden[j] >= 0) {
            projected.targets.push_back(project(state.d[j]));
        }
    }
    return projected;
}

std::vector<TargetOptions> materialize_options(
    const std::vector<std::uint64_t>& raw_targets,
    const TemplateTable& templates
) {
    std::set<std::uint64_t> distinct;
    for (const auto row : raw_targets) {
        if (std::popcount(row) >= 2) {
            distinct.insert(row);
        }
    }
    std::vector<TargetOptions> result;
    result.reserve(distinct.size());
    for (const auto row : distinct) {
        const unsigned weight = std::popcount(row);
        if (weight > 9) {
            continue;
        }
        std::array<unsigned, 9> support{};
        unsigned count = 0;
        for (auto value = row; value; value &= value - 1) {
            support[count++] = std::countr_zero(value);
        }
        TargetOptions target;
        target.row = row;
        target.options.reserve(templates[weight].size());
        for (const auto& source : templates[weight]) {
            ConcreteOption option;
            option.final_units = source.final_units;
            for (unsigned block = 0; block < source.count; ++block) {
                const auto& part = source.blocks[block];
                if (part.size == 1) {
                    continue;
                }
                int id = -1;
                if (part.size == 2) {
                    id = pair_id(
                        support[part.positions[0]], support[part.positions[1]]
                    );
                } else {
                    id = triple_id(
                        support[part.positions[0]], support[part.positions[1]],
                        support[part.positions[2]]
                    );
                }
                option.groups[option.group_count++] = static_cast<std::int16_t>(id);
            }
            target.options.push_back(option);
        }
        result.push_back(std::move(target));
    }
    return result;
}

int added_units(const ConcreteOption& option, const std::vector<std::uint8_t>& usage) {
    int result = option.final_units;
    for (unsigned i = 0; i < option.group_count; ++i) {
        if (usage[option.groups[i]] == 0) {
            result += group_cost_units(option.groups[i]);
        }
    }
    return result;
}

int reuse_score(
    const ConcreteOption& option,
    const std::vector<std::uint8_t>& usage,
    const std::vector<std::uint8_t>& frequency
) {
    int result = 0;
    for (unsigned i = 0; i < option.group_count; ++i) {
        const int id = option.groups[i];
        if (usage[id] == 0) {
            result += static_cast<int>(frequency[id]) / group_cost_units(id);
        }
    }
    return result;
}

GreedyCover greedy_cover(
    const std::vector<std::uint64_t>& raw_targets,
    const TemplateTable& templates
) {
    auto targets = materialize_options(raw_targets, templates);
    if (targets.empty()) {
        return GreedyCover{0, 0, 0, 0, 0};
    }
    std::vector<std::uint8_t> frequency(group_universe);
    for (const auto& target : targets) {
        std::array<unsigned, 9> support{};
        unsigned count = 0;
        for (auto row = target.row; row; row &= row - 1) {
            support[count++] = std::countr_zero(row);
        }
        for (unsigned a = 0; a < count; ++a) {
            for (unsigned b = a + 1; b < count; ++b) {
                ++frequency[pair_id(support[a], support[b])];
                for (unsigned c = b + 1; c < count; ++c) {
                    ++frequency[triple_id(support[a], support[b], support[c])];
                }
            }
        }
    }
    std::array<std::vector<unsigned>, 3> orders;
    for (auto& order : orders) {
        order.resize(targets.size());
        for (unsigned i = 0; i < targets.size(); ++i) {
            order[i] = i;
        }
    }
    std::stable_sort(orders[0].begin(), orders[0].end(), [&](unsigned a, unsigned b) {
        return std::tuple(targets[a].options.size(), targets[a].row) <
               std::tuple(targets[b].options.size(), targets[b].row);
    });
    std::stable_sort(orders[1].begin(), orders[1].end(), [&](unsigned a, unsigned b) {
        return std::tuple(std::popcount(targets[a].row), targets[a].row) >
               std::tuple(std::popcount(targets[b].row), targets[b].row);
    });

    GreedyCover best;
    for (const auto& order : orders) {
        std::vector<std::uint8_t> usage(group_universe);
        std::vector<unsigned> selected(targets.size());
        for (const auto target_index : order) {
            const auto& options = targets[target_index].options;
            int best_units = std::numeric_limits<int>::max();
            int best_reuse = -1;
            unsigned best_option = 0;
            for (unsigned option_index = 0; option_index < options.size(); ++option_index) {
                const int units = added_units(options[option_index], usage);
                const int reuse = reuse_score(options[option_index], usage, frequency);
                if (units < best_units || (units == best_units && reuse > best_reuse)) {
                    best_units = units;
                    best_reuse = reuse;
                    best_option = option_index;
                }
            }
            selected[target_index] = best_option;
            for (unsigned i = 0; i < options[best_option].group_count; ++i) {
                ++usage[options[best_option].groups[i]];
            }
        }

        // Coordinate descent preserves a concrete valid cover while exploiting
        // groups selected for other targets. Two passes capture almost all local
        // sharing without turning every annealing step into an exact SAT solve.
        for (unsigned pass = 0; pass < 2; ++pass) {
            bool changed = false;
            for (const auto target_index : order) {
                const auto& options = targets[target_index].options;
                const auto old = selected[target_index];
                for (unsigned i = 0; i < options[old].group_count; ++i) {
                    --usage[options[old].groups[i]];
                }
                int best_units = std::numeric_limits<int>::max();
                int best_reuse = -1;
                unsigned best_option = old;
                for (unsigned option_index = 0; option_index < options.size(); ++option_index) {
                    const int units = added_units(options[option_index], usage);
                    const int reuse = reuse_score(options[option_index], usage, frequency);
                    if (units < best_units || (units == best_units && reuse > best_reuse)) {
                        best_units = units;
                        best_reuse = reuse;
                        best_option = option_index;
                    }
                }
                selected[target_index] = best_option;
                for (unsigned i = 0; i < options[best_option].group_count; ++i) {
                    ++usage[options[best_option].groups[i]];
                }
                changed |= best_option != old;
            }
            if (!changed) {
                break;
            }
        }

        GreedyCover cover{0, 0, 0, 0, 0};
        for (int id = 0; id < group_universe; ++id) {
            if (usage[id] == 0) {
                continue;
            }
            cover.logic_units += group_cost_units(id);
            if (id < pair_universe) {
                ++cover.pair_groups;
            } else {
                ++cover.triple_groups;
            }
        }
        for (unsigned target = 0; target < targets.size(); ++target) {
            const auto units = targets[target].options[selected[target]].final_units;
            cover.logic_units += units;
            cover.final_xor2 += units == 1;
            cover.final_switch3 += units == 4;
        }
        if (cover.logic_units < best.logic_units) {
            best = cover;
        }
    }
    return best;
}

struct Score {
    int unsupported = 0;
    int active_hidden = 0;
    int distinct_targets = 0;
    int maximum = 0;
    int total_weight = 0;
    int optimistic_total_gate = 1000000;
    int greedy_logic_gate = 1000000;
    int greedy_total_gate = 1000000;
    int pair_groups = 0;
    int triple_groups = 0;
    int final_xor2 = 0;
    int final_switch3 = 0;

    auto key() const {
        return std::tie(unsupported, greedy_total_gate, optimistic_total_gate,
                        maximum, total_weight, distinct_targets, active_hidden);
    }
};

bool operator<(const Score& left, const Score& right) {
    return left.key() < right.key();
}

Score evaluate(
    const State& state,
    const std::array<std::uint32_t, visible>& a,
    const TemplateTable& templates
) {
    Score score;
    const auto projected = project_zero_hidden(state, a);
    score.active_hidden = projected.active_hidden;
    std::set<std::uint64_t> distinct;
    for (const auto row : projected.targets) {
        const int weight = std::popcount(row);
        score.unsupported += std::max(0, weight - 9);
        score.maximum = std::max(score.maximum, weight);
        score.total_weight += weight;
        if (weight >= 2) {
            distinct.insert(row);
        }
    }
    score.distinct_targets = static_cast<int>(distinct.size());
    score.optimistic_total_gate =
        198 + 5 * score.active_hidden + 3 * score.distinct_targets;
    if (score.unsupported == 0) {
        const auto cover = greedy_cover(projected.targets, templates);
        score.greedy_logic_gate = 3 * cover.logic_units;
        score.greedy_total_gate =
            198 + 5 * score.active_hidden + score.greedy_logic_gate;
        score.pair_groups = cover.pair_groups;
        score.triple_groups = cover.triple_groups;
        score.final_xor2 = cover.final_xor2;
        score.final_switch3 = cover.final_switch3;
    }
    return score;
}

double energy(const Score& score) {
    return 1000000.0 * score.unsupported +
           1000.0 * score.greedy_total_gate + score.total_weight;
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
    if ((generator() % 16) == 0) {
        return 0;
    }
    std::uint64_t row = 0;
    const unsigned weight = 1 + generator() % 4;
    while (std::popcount(row) < static_cast<int>(weight)) {
        row |= std::uint64_t{1} << (generator() % state_bits);
    }
    return row;
}

void canonicalize_inactive(State& state) {
    bool changed = true;
    while (changed) {
        changed = false;
        std::uint16_t active = 0;
        for (unsigned j = 0; j < hidden; ++j) {
            active |= static_cast<std::uint16_t>((state.d[j] != 0) << j);
        }
        const std::uint64_t keep = 0xffffffffu | (std::uint64_t{active} << visible);
        for (unsigned j = 0; j < hidden; ++j) {
            if (state.d[j] != 0) {
                const auto reduced = state.d[j] & keep;
                changed |= reduced != state.d[j];
                state.d[j] = reduced;
            }
        }
    }
    std::uint16_t active = 0;
    for (unsigned j = 0; j < hidden; ++j) {
        active |= static_cast<std::uint16_t>((state.d[j] != 0) << j);
    }
    for (auto& row : state.x) {
        row &= active;
    }
}

void compact_hidden(State& state) {
    canonicalize_inactive(state);
    std::array<int, hidden> mapping{};
    mapping.fill(-1);
    unsigned count = 0;
    for (unsigned old = 0; old < hidden; ++old) {
        if (state.d[old] != 0) {
            mapping[old] = static_cast<int>(count++);
        }
    }
    auto project = [&](std::uint64_t row) {
        std::uint64_t result = row & 0xffffffffu;
        for (unsigned old = 0; old < hidden; ++old) {
            if (mapping[old] >= 0 && ((row >> (visible + old)) & 1u)) {
                result |= std::uint64_t{1} << (visible + mapping[old]);
            }
        }
        return result;
    };
    std::array<std::uint64_t, hidden> new_d{};
    for (unsigned old = 0; old < hidden; ++old) {
        if (mapping[old] >= 0) {
            new_d[mapping[old]] = project(state.d[old]);
        }
    }
    for (auto& row : state.x) {
        row = static_cast<std::uint16_t>(project(std::uint64_t{row} << visible) >> visible);
    }
    state.d = new_d;
}

void enforce_active_count(
    State& state,
    int forced_active,
    std::mt19937_64& generator
) {
    compact_hidden(state);
    if (forced_active < 0) {
        return;
    }
    for (unsigned j = 0; j < hidden; ++j) {
        if (static_cast<int>(j) >= forced_active) {
            state.d[j] = 0;
        } else if (state.d[j] == 0) {
            // A visible source guarantees that canonical removal of inactive
            // high columns cannot erase a row that is required by fixed-k mode.
            state.d[j] = std::uint64_t{1} << (generator() % visible);
        }
    }
    canonicalize_inactive(state);
    for (int j = 0; j < forced_active; ++j) {
        if (state.d[j] == 0) {
            state.d[j] = std::uint64_t{1} << (generator() % visible);
        }
    }
}

void initialize(
    State& state,
    unsigned restart,
    std::mt19937_64& generator,
    const std::array<std::uint32_t, visible>& a,
    const std::vector<std::uint16_t>& candidate_masks,
    int forced_active
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
    constexpr std::array<std::uint16_t, visible> beam_x{
        0x002, 0x001, 0x020, 0x010, 0x008, 0x002, 0x000, 0x020,
        0x000, 0x008, 0x000, 0x000, 0x004, 0x000, 0x000, 0x000,
        0x000, 0x002, 0x001, 0x020, 0x010, 0x008, 0x002, 0x000,
        0x020, 0x004, 0x008, 0x000, 0x000, 0x000, 0x000, 0x000,
    };
    constexpr std::array<std::uint64_t, hidden> beam_d{
        0x00000084042, 0x00100440020, 0x00042003000, 0x00204400200,
        0x00800300100, 0x01001100080, 0x00000000000, 0x00000000000,
        0x00000000000, 0x00000000000,
    };
    // Exact pruned-38 point, including its four genuinely inactive rows.
    constexpr std::array<std::uint16_t, visible> pruned_x{
        0x000, 0x000, 0x001, 0x010, 0x084, 0x002, 0x001, 0x001,
        0x000, 0x200, 0x000, 0x001, 0x000, 0x204, 0x000, 0x000,
        0x000, 0x080, 0x206, 0x001, 0x010, 0x004, 0x006, 0x000,
        0x001, 0x010, 0x004, 0x000, 0x000, 0x000, 0x284, 0x000,
    };
    constexpr std::array<std::uint64_t, hidden> pruned_d{
        0x00001100080, 0x20004840000, 0x20204400000, 0x00000000000,
        0x01002200100, 0x00000000000, 0x00000000000, 0x00200022000,
        0x00000000000, 0x20400404000,
    };
    constexpr std::array<std::uint32_t, hidden> frontier_r{
        0x00002001, 0x00004002, 0x00010008, 0x00020010, 0x00040020,
        0x00080040, 0x00100080, 0x00800400, 0x04002000, 0x08004000,
    };
    if (restart == 0) {
        state.x = pruned_x;
        state.d = pruned_d;
        enforce_active_count(state, forced_active, generator);
        return;
    }
    if (restart == 1) {
        state.x = resume_x;
        state.d = resume_d;
        enforce_active_count(state, forced_active, generator);
        return;
    }
    if (restart == 2) {
        state.x = beam_x;
        state.d = beam_d;
        enforce_active_count(state, forced_active, generator);
        return;
    }
    for (unsigned j = 0; j < hidden; ++j) {
        if (restart < 6) {
            state.d[j] = frontier_r[j];
            if ((generator() % 5) == 0) {
                state.d[j] = 0;
            }
        } else {
            state.d[j] = random_sparse_row(generator);
        }
    }
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
    enforce_active_count(state, forced_active, generator);
}

void mutate(
    State& proposal,
    std::mt19937_64& generator,
    const std::vector<std::uint16_t>& candidate_masks,
    int forced_active
) {
    if ((generator() % 100) < 70) {
        auto& row = proposal.x[generator() % visible];
        if ((generator() % 100) < 75) {
            const unsigned limit = forced_active >= 0
                ? static_cast<unsigned>(forced_active) : hidden;
            if (limit == 0) {
                row = 0;
                return;
            }
            const unsigned bit = generator() % limit;
            if ((row >> bit) & 1u) {
                row ^= static_cast<std::uint16_t>(1u << bit);
            } else if (std::popcount(row) < 3) {
                row |= static_cast<std::uint16_t>(1u << bit);
            } else {
                std::array<unsigned, 3> set_bits{};
                unsigned count = 0;
                for (unsigned value = row; value; value &= value - 1) {
                    set_bits[count++] = std::countr_zero(value);
                }
                row ^= static_cast<std::uint16_t>(1u << set_bits[generator() % count]);
                row |= static_cast<std::uint16_t>(1u << bit);
            }
        } else {
            row = candidate_masks[generator() % candidate_masks.size()];
        }
        return;
    }
    const unsigned mutable_hidden = forced_active >= 0
        ? static_cast<unsigned>(forced_active) : hidden;
    if (mutable_hidden == 0) {
        return;
    }
    auto& row = proposal.d[generator() % mutable_hidden];
    if ((generator() % 100) < 8) {
        do {
            row = random_sparse_row(generator);
        } while (forced_active >= 0 && row == 0);
        return;
    }
    if (forced_active < 0 && (generator() % 100) < 4) {
        row = 0;
        return;
    }
    const unsigned bit = generator() % state_bits;
    if ((row >> bit) & 1u) {
        if (forced_active < 0 || std::popcount(row) > 1) {
            row ^= std::uint64_t{1} << bit;
        }
        return;
    }
    if (std::popcount(row) == 4) {
        std::array<unsigned, 4> set_bits{};
        unsigned count = 0;
        for (std::uint64_t value = row; value; value &= value - 1) {
            set_bits[count++] = std::countr_zero(value);
        }
        row ^= std::uint64_t{1} << set_bits[generator() % count];
    }
    row |= std::uint64_t{1} << bit;
}

void print_state(const State& state, const Score& score) {
    std::cout << "best unsupported=" << score.unsupported
              << " active_hidden=" << score.active_hidden
              << " distinct=" << score.distinct_targets
              << " max=" << score.maximum
              << " optimistic_total_gate=" << score.optimistic_total_gate
              << " greedy_logic_gate=" << score.greedy_logic_gate
              << " greedy_total_gate=" << score.greedy_total_gate
              << " pair_groups=" << score.pair_groups
              << " triple_groups=" << score.triple_groups
              << " final_xor2=" << score.final_xor2
              << " final_switch3=" << score.final_switch3
              << " total_weight=" << score.total_weight << " X=";
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
    std::cout << std::dec << '\n';
}

}  // namespace

int main(int argc, char** argv) {
    std::uint64_t iterations = 100'000;
    unsigned restarts = 4;
    std::uint64_t seed = 0x4310042u;
    int forced_active = -1;
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
        forced_active = std::stoi(argv[4]);
        if (forced_active < -1 || forced_active > static_cast<int>(hidden)) {
            throw std::invalid_argument("forced_active must be -1 or 0..10");
        }
    }

    const auto a = transition_rows();
    const auto templates = build_templates();
    const auto candidate_masks = masks();
    std::mt19937_64 generator(seed);
    std::uniform_real_distribution<double> unit(0.0, 1.0);
    State global_state;
    Score global_score;
    global_score.unsupported = std::numeric_limits<int>::max();

    for (unsigned restart = 0; restart < restarts; ++restart) {
        State current;
        initialize(current, restart, generator, a, candidate_masks, forced_active);
        auto current_score = evaluate(current, a, templates);
        if (current_score < global_score) {
            global_state = current;
            global_score = current_score;
            print_state(global_state, global_score);
        }
        for (std::uint64_t iteration = 0; iteration < iterations; ++iteration) {
            State proposal = current;
            mutate(proposal, generator, candidate_masks, forced_active);
            enforce_active_count(proposal, forced_active, generator);
            const auto proposal_score = evaluate(proposal, a, templates);
            const double progress = static_cast<double>(iteration) / iterations;
            const double temperature = 8000.0 * (1.0 - progress) + 10.0;
            const double delta = energy(proposal_score) - energy(current_score);
            if (delta <= 0.0 || unit(generator) < std::exp(-delta / temperature)) {
                current = proposal;
                current_score = proposal_score;
            }
            if (current_score < global_score) {
                global_state = current;
                global_score = current_score;
                print_state(global_state, global_score);
                if (global_score.unsupported == 0 &&
                    global_score.greedy_total_gate <= 430) {
                    return 0;
                }
            }
        }
    }
    print_state(global_state, global_score);
    return global_score.unsupported == 0 && global_score.greedy_total_gate <= 430 ? 0 : 2;
}
