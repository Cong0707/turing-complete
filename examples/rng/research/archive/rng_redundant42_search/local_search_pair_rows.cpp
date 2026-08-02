#include <algorithm>
#include <array>
#include <bit>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <random>
#include <sstream>
#include <string>
#include <tuple>
#include <vector>

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

struct State {
    std::array<std::uint32_t, aux> redundant{};
    std::array<std::uint16_t, bits> decoder{};
};

struct Score {
    int excess = 0;
    int maximum_weight = 0;
    int total_weight = 0;

    auto tie() const { return std::tie(excess, maximum_weight, total_weight); }
};

bool operator<(const Score& left, const Score& right) {
    return left.tie() < right.tie();
}

double energy(const Score& score) {
    return 1000.0 * score.excess + 20.0 * score.maximum_weight +
           score.total_weight;
}

std::uint16_t row_parity(
    std::uint32_t row,
    const std::array<std::uint16_t, bits>& decoder
) {
    std::uint16_t result = 0;
    while (row) {
        const auto low = row & (0u - row);
        result ^= decoder[std::countr_zero(low)];
        row ^= low;
    }
    return result;
}

Score evaluate(
    const State& state,
    const std::array<std::uint32_t, bits>& transition
) {
    Score score;
    auto account = [&score](int weight) {
        score.excess += std::max(0, weight - 4);
        score.maximum_weight = std::max(score.maximum_weight, weight);
        score.total_weight += weight;
    };

    for (unsigned index = 0; index < bits; ++index) {
        std::uint32_t encoded = transition[index];
        for (unsigned row = 0; row < aux; ++row) {
            if ((state.decoder[index] >> row) & 1u) {
                encoded ^= state.redundant[row];
            }
        }
        account(
            std::popcount(encoded) +
            std::popcount(row_parity(encoded, state.decoder))
        );
        account(1 + std::popcount(state.decoder[index]));
    }

    for (const auto row : state.redundant) {
        account(
            std::popcount(row) +
            std::popcount(row_parity(row, state.decoder))
        );
    }
    return score;
}

std::uint32_t random_pair(std::mt19937_64& generator) {
    std::uniform_int_distribution<unsigned> bit(0, bits - 1);
    unsigned left = bit(generator);
    unsigned right = bit(generator);
    while (left == right) {
        right = bit(generator);
    }
    return (std::uint32_t{1} << left) ^ (std::uint32_t{1} << right);
}

std::vector<std::uint16_t> decoder_masks() {
    std::vector<std::uint16_t> result;
    for (unsigned value = 0; value < (1u << aux); ++value) {
        if (std::popcount(value) <= 3) {
            result.push_back(static_cast<std::uint16_t>(value));
        }
    }
    return result;
}

void initialize_decoder(
    State& state,
    const std::array<std::uint32_t, bits>& transition,
    const std::vector<std::uint16_t>& masks,
    std::mt19937_64& generator
) {
    std::shuffle(state.decoder.begin(), state.decoder.end(), generator);
    for (unsigned index = 0; index < bits; ++index) {
        int best = std::numeric_limits<int>::max();
        std::vector<std::uint16_t> choices;
        for (const auto mask : masks) {
            std::uint32_t encoded = transition[index];
            for (unsigned row = 0; row < aux; ++row) {
                if ((mask >> row) & 1u) {
                    encoded ^= state.redundant[row];
                }
            }
            const int weight = std::popcount(encoded);
            if (weight < best) {
                best = weight;
                choices.clear();
            }
            if (weight == best) {
                choices.push_back(mask);
            }
        }
        state.decoder[index] = choices[generator() % choices.size()];
    }
}

void print_state(const State& state, const Score& score) {
    std::cout << "best excess=" << score.excess
              << " max_weight=" << score.maximum_weight
              << " total_weight=" << score.total_weight << " R=";
    for (unsigned index = 0; index < aux; ++index) {
        if (index) {
            std::cout << ',';
        }
        std::cout << std::hex << std::setw(8) << std::setfill('0')
                  << state.redundant[index];
    }
    std::cout << " V=";
    for (unsigned index = 0; index < bits; ++index) {
        if (index) {
            std::cout << ',';
        }
        std::cout << std::hex << std::setw(3) << std::setfill('0')
                  << state.decoder[index];
    }
    std::cout << std::dec << '\n';
}

}  // namespace

int main(int argc, char** argv) {
    std::uint64_t iterations = 2'000'000;
    unsigned restarts = 24;
    std::uint64_t seed = 0x42d3a91u;
    if (argc > 1) {
        iterations = std::stoull(argv[1]);
    }
    if (argc > 2) {
        restarts = static_cast<unsigned>(std::stoul(argv[2]));
    }
    if (argc > 3) {
        seed = std::stoull(argv[3]);
    }

    const auto transition = transition_rows();
    const auto masks = decoder_masks();
    std::mt19937_64 generator(seed);
    std::uniform_real_distribution<double> unit(0.0, 1.0);
    State global_best;
    Score global_score{std::numeric_limits<int>::max(),
                       std::numeric_limits<int>::max(),
                       std::numeric_limits<int>::max()};

    for (unsigned restart = 0; restart < restarts; ++restart) {
        State current;
        if (restart == 0) {
            constexpr std::array<unsigned, aux> initial{
                0, 1, 3, 4, 5, 6, 7, 10, 13, 14
            };
            for (unsigned index = 0; index < aux; ++index) {
                current.redundant[index] =
                    (std::uint32_t{1} << initial[index]) ^
                    (std::uint32_t{1} << (initial[index] + 13));
            }
        } else {
            for (auto& row : current.redundant) {
                row = random_pair(generator);
            }
        }
        initialize_decoder(current, transition, masks, generator);
        auto current_score = evaluate(current, transition);

        for (std::uint64_t iteration = 0; iteration < iterations; ++iteration) {
            State proposal = current;
            if ((generator() % 100) < 82) {
                const unsigned index = generator() % bits;
                std::uint16_t best_mask = proposal.decoder[index];
                auto best_score = current_score;
                const unsigned trials = 12;
                for (unsigned trial = 0; trial < trials; ++trial) {
                    proposal.decoder[index] = masks[generator() % masks.size()];
                    const auto trial_score = evaluate(proposal, transition);
                    if (trial_score < best_score) {
                        best_score = trial_score;
                        best_mask = proposal.decoder[index];
                    }
                }
                proposal.decoder[index] = best_mask;
            } else {
                proposal.redundant[generator() % aux] = random_pair(generator);
            }

            const auto proposal_score = evaluate(proposal, transition);
            const double progress = static_cast<double>(iteration) / iterations;
            const double temperature = 12.0 * (1.0 - progress) + 0.15;
            const double delta = energy(proposal_score) - energy(current_score);
            if (delta <= 0.0 || unit(generator) < std::exp(-delta / temperature)) {
                current = proposal;
                current_score = proposal_score;
            }
            if (current_score < global_score) {
                global_best = current;
                global_score = current_score;
                print_state(global_best, global_score);
                if (global_score.excess == 0) {
                    return 0;
                }
            }
        }
    }
    print_state(global_best, global_score);
    return global_score.excess == 0 ? 0 : 2;
}
