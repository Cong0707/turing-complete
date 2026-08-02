#pragma once

#include <array>
#include <bit>
#include <cmath>
#include <cstdint>
#include <vector>

// Fast estimates calibrated against the exact XOR2/Switch-XOR3 cost objective.
// Input targets must already be projected onto the active state columns and
// deduplicated, with constants and weight-one rows removed.
namespace rng_proxy_v2 {

struct Estimate {
    int unsupported = 0;
    int logic_milliunits = 0;  // one unit is three gates
    int logic_gate = 0;
    int total_gate = 0;
};

inline int rounded_logic_gate(int milliunits) {
    return (3 * milliunits + 500) / 1000;
}

inline Estimate weight_estimate(
    const std::vector<std::uint64_t>& targets,
    int active_hidden
) {
    // Effective coefficients from proxy_v2_cost_dataset_hq.json.  Folding the
    // standalone partition cost into each weight makes this only eight adds.
    constexpr std::array<int, 10> coefficient{
        0, 0, 984, 1819, 1884, 4421, 4748, 7215, 10530, 12377,
    };
    Estimate result;
    result.logic_milliunits = 9922;
    for (const auto target : targets) {
        const auto weight = std::popcount(target);
        if (weight > 9) {
            result.unsupported += weight - 9;
        } else if (weight >= 2) {
            result.logic_milliunits += coefficient[weight];
        }
    }
    result.logic_gate = rounded_logic_gate(result.logic_milliunits);
    result.total_gate = (32 + active_hidden) * 5 + 38 + result.logic_gate;
    return result;
}

inline Estimate pair_estimate(
    const std::vector<std::uint64_t>& targets,
    int active_hidden
) {
    constexpr std::array<int, 10> coefficient{
        0, 0, 1063, 1639, 1756, 4066, 4235, 6563, 9425, 11347,
    };
    constexpr int max_bits = 42;
    std::array<std::uint16_t, max_bits * max_bits> frequency{};
    std::vector<std::uint64_t> forced_pairs;
    Estimate result;
    result.logic_milliunits = 6707;

    for (const auto target : targets) {
        const auto weight = std::popcount(target);
        if (weight > 9) {
            result.unsupported += weight - 9;
            continue;
        }
        if (weight >= 2) {
            result.logic_milliunits += coefficient[weight];
        }
        if (weight == 2) {
            forced_pairs.push_back(target);
        }
        std::array<unsigned, max_bits> bits{};
        unsigned count = 0;
        for (auto value = target; value; value &= value - 1) {
            bits[count++] = std::countr_zero(value);
        }
        for (unsigned left = 0; left < count; ++left) {
            for (unsigned right = left + 1; right < count; ++right) {
                ++frequency[bits[left] * max_bits + bits[right]];
            }
        }
    }

    int forced_hits = 0;
    for (const auto target : targets) {
        if (std::popcount(target) < 3) {
            continue;
        }
        for (const auto pair : forced_pairs) {
            forced_hits += (pair & target) == pair;
        }
    }
    int pair_repeat = 0;
    int pair_ge2 = 0;
    int pair_ge3 = 0;
    for (const auto count : frequency) {
        if (count >= 2) {
            pair_repeat += count - 1;
            ++pair_ge2;
        }
        pair_ge3 += count >= 3;
    }
    result.logic_milliunits += 32 * forced_hits - 13 * pair_repeat +
                               210 * pair_ge2 - 191 * pair_ge3;
    result.logic_gate = rounded_logic_gate(result.logic_milliunits);
    result.total_gate = (32 + active_hidden) * 5 + 38 + result.logic_gate;
    return result;
}

}  // namespace rng_proxy_v2
