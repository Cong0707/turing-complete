#include <algorithm>
#include <array>
#include <bit>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <random>
#include <tuple>
#include <unordered_set>
#include <vector>

namespace {

constexpr int kBits = 32;
constexpr int kAux = 10;
using Rows32 = std::array<std::uint32_t, kBits>;
using AuxRows = std::array<std::uint32_t, kAux>;

std::uint32_t xorshift32(std::uint32_t value) {
    value ^= value >> 13;
    value ^= value << 17;
    value ^= value >> 5;
    return value;
}

Rows32 transition_rows() {
    Rows32 rows{};
    for (int source = 0; source < kBits; ++source) {
        const auto value = xorshift32(std::uint32_t{1} << source);
        for (int output = 0; output < kBits; ++output) {
            rows[output] |= ((value >> output) & 1U) << source;
        }
    }
    return rows;
}

std::uint32_t apply_row(std::uint32_t row, const Rows32& matrix) {
    std::uint32_t result = 0;
    while (row) {
        const int bit = std::countr_zero(row);
        result ^= matrix[bit];
        row &= row - 1;
    }
    return result;
}

struct Score {
    int heavy = 0;
    int squared_excess = 0;
    int maximum = 0;
    int total = 0;

    auto key() const {
        return std::tuple(heavy, squared_excess, maximum, total);
    }
    bool feasible() const { return heavy == 0; }
};

bool operator<(const Score& left, const Score& right) {
    return left.key() < right.key();
}

double energy(const Score& score) {
    return score.heavy * 15000.0 + score.squared_excess * 2500.0 +
           score.maximum * 50.0 + score.total;
}

struct Evaluator {
    Rows32 A = transition_rows();
    std::vector<std::uint16_t> masks;
    std::vector<std::uint8_t> mask_weights;

    Evaluator() {
        for (std::uint16_t mask = 0; mask < (1U << kAux); ++mask) {
            const int weight = std::popcount(mask);
            if (weight <= 4) {
                masks.push_back(mask);
                mask_weights.push_back(static_cast<std::uint8_t>(weight));
            }
        }
    }

    Score operator()(const AuxRows& rows) const {
        std::array<std::uint32_t, 1U << kAux> combinations{};
        for (std::uint16_t mask = 1; mask < combinations.size(); ++mask) {
            const int bit = std::countr_zero(mask);
            combinations[mask] = combinations[mask ^ (1U << bit)] ^ rows[bit];
        }

        Score score;
        const auto account = [&](std::uint32_t target, Score& current) {
            int best = 33;
            for (std::size_t index = 0; index < masks.size(); ++index) {
                const int weight = mask_weights[index] +
                                   std::popcount(target ^ combinations[masks[index]]);
                best = std::min(best, weight);
                if (best <= 2) {
                    break;
                }
            }
            current.heavy += best > 4;
            const int excess = std::max(0, best - 4);
            current.squared_excess += excess * excess;
            current.maximum = std::max(current.maximum, best);
            current.total += best;
        };

        for (const auto row : A) {
            account(row, score);
        }
        for (const auto row : rows) {
            account(apply_row(row, A), score);
        }
        return score;
    }
};

std::vector<std::uint32_t> candidate_pool(const Rows32& A) {
    std::unordered_set<std::uint32_t> unique;
    for (int left = 0; left < kBits; ++left) {
        for (int right = left + 1; right < kBits; ++right) {
            unique.insert((std::uint32_t{1} << left) |
                          (std::uint32_t{1} << right));
        }
    }
    for (const auto row : A) {
        std::vector<int> bits;
        for (auto remaining = row; remaining; remaining &= remaining - 1) {
            bits.push_back(std::countr_zero(remaining));
        }
        for (int a = 0; a < static_cast<int>(bits.size()); ++a) {
            for (int b = a + 1; b < static_cast<int>(bits.size()); ++b) {
                for (int c = b + 1; c < static_cast<int>(bits.size()); ++c) {
                    unique.insert((std::uint32_t{1} << bits[a]) |
                                  (std::uint32_t{1} << bits[b]) |
                                  (std::uint32_t{1} << bits[c]));
                    for (int d = c + 1; d < static_cast<int>(bits.size()); ++d) {
                        unique.insert((std::uint32_t{1} << bits[a]) |
                                      (std::uint32_t{1} << bits[b]) |
                                      (std::uint32_t{1} << bits[c]) |
                                      (std::uint32_t{1} << bits[d]));
                    }
                }
            }
        }
    }
    std::vector<std::uint32_t> result(unique.begin(), unique.end());
    std::sort(result.begin(), result.end());
    return result;
}

AuxRows initial_rows() {
    return {
        0x80004000U, 0x40002000U, 0x00400020U, 0x00800040U,
        0x01000080U, 0x00100008U, 0x00200010U, 0x00080004U,
        0x00040002U, 0x02000100U,
    };
}

void print_best(std::uint64_t step, const Score& score, const AuxRows& rows) {
    std::printf("best step=%llu heavy=%d excess=%d max=%d total=%d R=",
                static_cast<unsigned long long>(step), score.heavy,
                score.squared_excess, score.maximum, score.total);
    for (int index = 0; index < kAux; ++index) {
        std::printf("%s%08x", index ? "," : "", rows[index]);
    }
    std::printf("\n");
    std::fflush(stdout);
}

}  // namespace

int main(int argc, char** argv) {
    const std::uint64_t seed = argc > 1 ? std::strtoull(argv[1], nullptr, 0) : 0x42U;
    const std::uint64_t steps = argc > 2 ? std::strtoull(argv[2], nullptr, 0) : 300000U;
    const std::uint64_t restart_period = argc > 3 ? std::strtoull(argv[3], nullptr, 0) : 25000U;

    Evaluator evaluate;
    const auto pool = candidate_pool(evaluate.A);
    std::mt19937_64 random(seed);
    std::uniform_real_distribution<double> unit(0.0, 1.0);

    AuxRows global_rows = initial_rows();
    Score global_score = evaluate(global_rows);
    print_best(0, global_score, global_rows);

    AuxRows current = global_rows;
    Score current_score = global_score;
    for (std::uint64_t step = 1; step <= steps; ++step) {
        if (restart_period && step % restart_period == 0) {
            current = global_rows;
            for (int perturb = 0; perturb < 3; ++perturb) {
                current[random() % kAux] = pool[random() % pool.size()];
            }
            current_score = evaluate(current);
        }

        AuxRows proposal = current;
        const int row = static_cast<int>(random() % kAux);
        const auto mode = random() % 100;
        if (mode < 82) {
            proposal[row] = pool[random() % pool.size()];
        } else if (mode < 92) {
            proposal[row] ^= std::uint32_t{1} << (random() % kBits);
        } else {
            int other = static_cast<int>(random() % (kAux - 1));
            other += other >= row;
            proposal[row] ^= proposal[other];
        }
        if (proposal[row] == 0 ||
            std::find(proposal.begin(), proposal.end(), proposal[row]) !=
                proposal.begin() + row) {
            continue;
        }

        const Score proposal_score = evaluate(proposal);
        if (proposal_score < global_score) {
            global_score = proposal_score;
            global_rows = proposal;
            print_best(step, global_score, global_rows);
            if (global_score.feasible()) {
                return 0;
            }
        }

        const double phase = restart_period
            ? static_cast<double>(step % restart_period) / restart_period
            : static_cast<double>(step) / steps;
        const double temperature = 9000.0 * std::pow(0.002, phase) + 2.0;
        const double delta = energy(proposal_score) - energy(current_score);
        if (delta <= 0.0 || unit(random) < std::exp(-delta / temperature)) {
            current = proposal;
            current_score = proposal_score;
        }
    }

    print_best(steps, global_score, global_rows);
    return global_score.feasible() ? 0 : 2;
}
