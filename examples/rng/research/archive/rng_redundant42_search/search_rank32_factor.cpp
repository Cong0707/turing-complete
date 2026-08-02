#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <limits>
#include <numeric>
#include <tuple>
#include <vector>

namespace {

constexpr std::uint32_t mask32 = 0xffffffffu;

std::uint32_t xorshift32(std::uint32_t value) {
    value ^= value >> 13;
    value ^= value << 17;
    value ^= value >> 5;
    return value;
}

std::array<std::uint32_t, 32> transition_rows() {
    std::array<std::uint32_t, 32> rows{};
    for (unsigned source = 0; source < 32; ++source) {
        const auto output = xorshift32(std::uint32_t{1} << source);
        for (unsigned target = 0; target < 32; ++target) {
            if ((output >> target) & 1u) {
                rows[target] |= std::uint32_t{1} << source;
            }
        }
    }
    return rows;
}

struct Candidate {
    int residual_sum = 0;
    int capped_domain_sum = 0;
    int minimum_domain = 0;
    std::array<unsigned, 10> selected{};
};

bool better(const Candidate& left, const Candidate& right) {
    return std::tie(left.residual_sum, left.capped_domain_sum, left.selected) <
           std::tie(right.residual_sum, right.capped_domain_sum, right.selected);
}

}  // namespace

int main() {
    const auto a_rows = transition_rows();
    std::array<std::uint32_t, 19> first_pairs{};
    for (unsigned index = 0; index < first_pairs.size(); ++index) {
        first_pairs[index] = (std::uint32_t{1} << index) ^
                             (std::uint32_t{1} << (index + 13));
    }

    std::vector<Candidate> frontier;
    std::uint64_t tested = 0;
    std::uint64_t support_feasible = 0;

    for (unsigned selection = 0; selection < (1u << 19); ++selection) {
        if (std::popcount(selection) != 10) {
            continue;
        }
        ++tested;

        Candidate candidate;
        unsigned cursor = 0;
        std::array<std::uint32_t, 10> rows{};
        for (unsigned index = 0; index < 19; ++index) {
            if ((selection >> index) & 1u) {
                candidate.selected[cursor] = index;
                rows[cursor] = first_pairs[index];
                ++cursor;
            }
        }

        std::array<std::uint32_t, 176> combinations{};
        unsigned combination_count = 0;
        for (unsigned subset = 0; subset < (1u << 10); ++subset) {
            if (std::popcount(subset) > 3) {
                continue;
            }
            std::uint32_t value = 0;
            for (unsigned index = 0; index < 10; ++index) {
                if ((subset >> index) & 1u) {
                    value ^= rows[index];
                }
            }
            combinations[combination_count++] = value;
        }

        bool feasible = true;
        candidate.minimum_domain = std::numeric_limits<int>::max();
        for (const auto target : a_rows) {
            int best_weight = 33;
            int domain = 0;
            for (unsigned index = 0; index < combination_count; ++index) {
                const int weight = std::popcount(target ^ combinations[index]);
                best_weight = std::min(best_weight, weight);
                domain += weight <= 4;
            }
            if (best_weight > 4) {
                feasible = false;
                break;
            }
            candidate.residual_sum += best_weight;
            candidate.capped_domain_sum -= std::min(domain, 20);
            candidate.minimum_domain = std::min(candidate.minimum_domain, domain);
        }
        if (!feasible) {
            continue;
        }
        ++support_feasible;

        frontier.push_back(candidate);
        std::sort(frontier.begin(), frontier.end(), better);
        if (frontier.size() > 1000) {
            frontier.resize(1000);
        }
    }

    std::cout << "tested=" << tested << " support_feasible=" << support_feasible
              << " frontier=" << frontier.size() << '\n';
    for (const auto& candidate : frontier) {
        std::cout << "score=" << candidate.residual_sum
                  << " domain_score=" << -candidate.capped_domain_sum
                  << " min_domain=" << candidate.minimum_domain << " rows=";
        for (unsigned index = 0; index < candidate.selected.size(); ++index) {
            if (index) {
                std::cout << ',';
            }
            std::cout << candidate.selected[index];
        }
        std::cout << '\n';
    }
}
