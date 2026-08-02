#include <algorithm>
#include <array>
#include <bit>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <random>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_set>

namespace {

constexpr unsigned bits = 32;
constexpr unsigned aux = 10;

std::uint32_t xorshift32(std::uint32_t value) {
    value ^= value >> 13;
    value ^= value << 17;
    value ^= value >> 5;
    return value;
}

std::array<std::uint32_t, bits> transition_rows() {
    std::array<std::uint32_t, bits> rows{};
    for (unsigned source = 0; source < bits; ++source) {
        const auto output = xorshift32(std::uint32_t{1} << source);
        for (unsigned target = 0; target < bits; ++target) {
            if ((output >> target) & 1u) {
                rows[target] |= std::uint32_t{1} << source;
            }
        }
    }
    return rows;
}

using Dictionary = std::array<std::uint32_t, aux>;

struct Quality {
    int support_excess = 0;
    int residual_sum = 0;
    int capped_domains = 0;
};

double energy(const Quality& quality) {
    return 1000.0 * quality.support_excess + quality.residual_sum -
           0.02 * quality.capped_domains;
}

Quality evaluate(
    const Dictionary& dictionary,
    const std::array<std::uint32_t, bits>& transition
) {
    std::array<std::uint32_t, 176> combinations{};
    unsigned count = 0;
    for (unsigned mask = 0; mask < (1u << aux); ++mask) {
        if (std::popcount(mask) > 3) {
            continue;
        }
        std::uint32_t value = 0;
        for (unsigned index = 0; index < aux; ++index) {
            if ((mask >> index) & 1u) {
                value ^= dictionary[index];
            }
        }
        combinations[count++] = value;
    }

    Quality result;
    for (const auto target : transition) {
        int best = 33;
        int domain = 0;
        for (unsigned index = 0; index < count; ++index) {
            const int weight = std::popcount(target ^ combinations[index]);
            best = std::min(best, weight);
            domain += weight <= 4;
        }
        result.support_excess += std::max(0, best - 4);
        result.residual_sum += best;
        result.capped_domains += std::min(domain, 20);
    }
    return result;
}

std::uint32_t random_row(std::mt19937_64& generator, unsigned maximum_weight) {
    const unsigned weight = 2 + generator() % (maximum_weight - 1);
    std::uint32_t result = 0;
    while (static_cast<unsigned>(std::popcount(result)) < weight) {
        result |= std::uint32_t{1} << (generator() % bits);
    }
    return result;
}

std::string key(const Dictionary& dictionary) {
    std::string result;
    result.reserve(aux * 8);
    for (const auto row : dictionary) {
        for (unsigned byte = 0; byte < 4; ++byte) {
            result.push_back(static_cast<char>((row >> (8 * byte)) & 0xffu));
        }
    }
    return result;
}

void print_candidate(const Dictionary& dictionary, const Quality& quality) {
    std::cout << "support_excess=" << quality.support_excess
              << " residual_sum=" << quality.residual_sum
              << " domain_score=" << quality.capped_domains << " R=";
    for (unsigned index = 0; index < aux; ++index) {
        if (index) {
            std::cout << ',';
        }
        std::cout << std::hex << std::setw(8) << std::setfill('0')
                  << dictionary[index];
    }
    std::cout << std::dec << '\n';
}

}  // namespace

int main(int argc, char** argv) {
    std::uint64_t iterations = 5'000'000;
    std::uint64_t seed = 0x420061u;
    unsigned target = 2000;
    unsigned maximum_weight = 2;
    if (argc > 1) {
        iterations = std::stoull(argv[1]);
    }
    if (argc > 2) {
        seed = std::stoull(argv[2]);
    }
    if (argc > 3) {
        target = static_cast<unsigned>(std::stoul(argv[3]));
    }
    if (argc > 4) {
        maximum_weight = static_cast<unsigned>(std::stoul(argv[4]));
    }
    if (maximum_weight < 2 || maximum_weight > 4) {
        throw std::invalid_argument("maximum row weight must be in [2,4]");
    }

    const auto transition = transition_rows();
    std::mt19937_64 generator(seed);
    std::uniform_real_distribution<double> unit(0.0, 1.0);
    constexpr std::array<unsigned, aux> initial_indices{
        0, 1, 3, 4, 5, 6, 7, 10, 13, 14
    };
    Dictionary current{};
    for (unsigned index = 0; index < aux; ++index) {
        current[index] =
            (std::uint32_t{1} << initial_indices[index]) ^
            (std::uint32_t{1} << (initial_indices[index] + 13));
    }
    std::sort(current.begin(), current.end());
    auto current_quality = evaluate(current, transition);

    std::unordered_set<std::string> emitted;
    if (current_quality.support_excess == 0) {
        emitted.insert(key(current));
        print_candidate(current, current_quality);
    }

    std::uint64_t last_new = 0;
    for (std::uint64_t iteration = 0;
         iteration < iterations && emitted.size() < target;
         ++iteration) {
        Dictionary proposal = current;
        proposal[generator() % aux] = random_row(generator, maximum_weight);
        std::sort(proposal.begin(), proposal.end());
        if (std::adjacent_find(proposal.begin(), proposal.end()) != proposal.end()) {
            continue;
        }
        const auto proposal_quality = evaluate(proposal, transition);
        const double delta = energy(proposal_quality) - energy(current_quality);
        const double temperature = iteration - last_new > 100'000 ? 20.0 : 2.0;
        if (delta <= 0.0 || unit(generator) < std::exp(-delta / temperature)) {
            current = proposal;
            current_quality = proposal_quality;
        }
        if (current_quality.support_excess == 0 &&
            emitted.insert(key(current)).second) {
            print_candidate(current, current_quality);
            last_new = iteration;
        }
        if (iteration - last_new > 500'000) {
            for (auto& row : current) {
                row = random_row(generator, maximum_weight);
            }
            std::sort(current.begin(), current.end());
            current_quality = evaluate(current, transition);
            last_new = iteration;
        }
    }
    std::cerr << "iterations=" << iterations << " emitted=" << emitted.size()
              << " seed=" << seed << '\n';
    return 0;
}
