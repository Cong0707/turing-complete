#include <algorithm>
#include <array>
#include <bit>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <limits>
#include <random>
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
    std::array<std::uint32_t, aux> r{};
    std::array<std::uint16_t, bits> x{};
};

struct Score {
    int excess = 0;
    int maximum = 0;
    int total = 0;
    int undecodable = 32;

    auto key() const { return std::tie(excess, maximum, undecodable, total); }
};

bool operator<(const Score& left, const Score& right) {
    return left.key() < right.key();
}

std::uint16_t row_times_x(
    std::uint32_t row,
    const std::array<std::uint16_t, bits>& x
) {
    std::uint16_t result = 0;
    while (row) {
        const auto low = row & (0u - row);
        result ^= x[std::countr_zero(low)];
        row ^= low;
    }
    return result;
}

std::uint32_t xor_r(
    std::uint16_t mask,
    const std::array<std::uint32_t, aux>& r
) {
    std::uint32_t result = 0;
    while (mask) {
        const auto low = static_cast<std::uint16_t>(
            mask & static_cast<std::uint16_t>(0u - mask)
        );
        result ^= r[std::countr_zero(low)];
        mask ^= low;
    }
    return result;
}

std::array<std::uint32_t, bits + aux> encoding_rows(
    const State& state,
    const std::array<std::uint32_t, bits>& a
) {
    std::array<std::uint32_t, bits + aux> e{};
    for (unsigned i = 0; i < bits; ++i) {
        e[i] = a[i] ^ xor_r(state.x[i], state.r);
    }
    std::copy(state.r.begin(), state.r.end(), e.begin() + bits);
    return e;
}

bool representable_at_most_four(
    std::uint32_t target,
    const std::array<std::uint32_t, bits + aux>& rows
) {
    for (unsigned i = 0; i < rows.size(); ++i) {
        if (rows[i] == target) return true;
    }
    std::vector<std::uint32_t> pairs;
    pairs.reserve(rows.size() * (rows.size() - 1) / 2);
    for (unsigned i = 0; i < rows.size(); ++i) {
        for (unsigned j = i + 1; j < rows.size(); ++j) {
            const auto value = rows[i] ^ rows[j];
            if (value == target) return true;
            pairs.push_back(value);
        }
    }
    std::sort(pairs.begin(), pairs.end());
    pairs.erase(std::unique(pairs.begin(), pairs.end()), pairs.end());
    for (const auto left : pairs) {
        if (std::binary_search(pairs.begin(), pairs.end(), target ^ left)) {
            return true;
        }
    }
    // A triple is covered by a singleton plus a pair.  The pair-pair check
    // above covers four terms (and harmless cancellations), while this loop
    // is retained for clarity when the two pair sets overlap.
    for (const auto row : rows) {
        if (std::binary_search(pairs.begin(), pairs.end(), target ^ row)) {
            return true;
        }
    }
    return false;
}

Score evaluate(
    const State& state,
    const std::array<std::uint32_t, bits>& a,
    bool check_decoder
) {
    Score score;
    auto account = [&](int weight) {
        score.excess += std::max(0, weight - 4);
        score.maximum = std::max(score.maximum, weight);
        score.total += weight;
    };
    const auto e = encoding_rows(state, a);
    for (const auto row : e) {
        account(std::popcount(row) + std::popcount(row_times_x(row, state.x)));
    }
    if (check_decoder && score.excess == 0) {
        score.undecodable = 0;
        for (const auto target : a) {
            score.undecodable += !representable_at_most_four(target, e);
        }
    }
    return score;
}

double energy(const Score& score) {
    return 100000.0 * score.excess + 1000.0 * score.maximum + score.total;
}

std::uint32_t random_sparse_r(std::mt19937_64& generator) {
    std::uint32_t row = 0;
    const unsigned weight = 1 + generator() % 4;
    while (std::popcount(row) < static_cast<int>(weight)) {
        row |= std::uint32_t{1} << (generator() % bits);
    }
    return row;
}

void initialize(State& state, unsigned restart, std::mt19937_64& generator) {
    constexpr std::array<std::uint32_t, aux> nearest_r{
        0x00042000, 0x00200100, 0x00010008, 0x00020010, 0x40000010,
        0x00080040, 0x00100080, 0x00800400, 0x04002000, 0x08004000,
    };
    constexpr std::array<std::uint16_t, bits> nearest_x{
        0x201, 0x020, 0x040, 0x000, 0x008, 0x080, 0x020, 0x040,
        0x100, 0x280, 0x000, 0x000, 0x110, 0x100, 0x200, 0x004,
        0x008, 0x019, 0x020, 0x060, 0x046, 0x108, 0x280, 0x000,
        0x040, 0x100, 0x200, 0x080, 0x000, 0x000, 0x100, 0x200,
    };
    if (restart == 0) {
        state.r = nearest_r;
        state.x = nearest_x;
        return;
    }
    for (auto& row : state.r) row = random_sparse_r(generator);
    for (auto& row : state.x) row = static_cast<std::uint16_t>(generator() & 0x3ffu);
}

void mutate(State& state, std::mt19937_64& generator) {
    if ((generator() % 100) < 84) {
        auto& row = state.x[generator() % bits];
        if ((generator() % 100) < 70) {
            row ^= static_cast<std::uint16_t>(1u << (generator() % aux));
        } else {
            row = static_cast<std::uint16_t>(generator() & 0x3ffu);
        }
    } else {
        auto& row = state.r[generator() % aux];
        const unsigned bit = generator() % bits;
        if ((row >> bit) & 1u) {
            if (std::popcount(row) > 1) row ^= std::uint32_t{1} << bit;
        } else {
            if (std::popcount(row) == 4) {
                std::vector<unsigned> present;
                for (auto value = row; value; value &= value - 1) {
                    present.push_back(std::countr_zero(value));
                }
                row ^= std::uint32_t{1} << present[generator() % present.size()];
            }
            row |= std::uint32_t{1} << bit;
        }
    }
}

void print(const State& state, const Score& score) {
    std::cout << "best excess=" << score.excess << " max=" << score.maximum
              << " total=" << score.total << " undecodable=" << score.undecodable
              << " R=";
    for (unsigned i = 0; i < aux; ++i) {
        if (i) std::cout << ',';
        std::cout << std::hex << std::setw(8) << std::setfill('0') << state.r[i];
    }
    std::cout << " X=";
    for (unsigned i = 0; i < bits; ++i) {
        if (i) std::cout << ',';
        std::cout << std::hex << std::setw(3) << std::setfill('0') << state.x[i];
    }
    std::cout << std::dec << '\n' << std::flush;
}

}  // namespace

int main(int argc, char** argv) {
    std::uint64_t iterations = 2'000'000;
    unsigned restarts = 16;
    std::uint64_t seed = 0xdec042u;
    if (argc > 1) iterations = std::stoull(argv[1]);
    if (argc > 2) restarts = static_cast<unsigned>(std::stoul(argv[2]));
    if (argc > 3) seed = std::stoull(argv[3]);

    const auto a = transition_rows();
    std::mt19937_64 generator(seed);
    std::uniform_real_distribution<double> unit(0.0, 1.0);
    State global;
    Score global_score;
    global_score.excess = std::numeric_limits<int>::max();

    for (unsigned restart = 0; restart < restarts; ++restart) {
        State current;
        initialize(current, restart, generator);
        auto current_score = evaluate(current, a, false);
        for (std::uint64_t iteration = 0; iteration < iterations; ++iteration) {
            State proposal = current;
            mutate(proposal, generator);
            const auto proposal_score = evaluate(proposal, a, false);
            const double progress = static_cast<double>(iteration) / iterations;
            const double temperature = 12000.0 * (1.0 - progress) + 20.0;
            const double delta = energy(proposal_score) - energy(current_score);
            if (delta <= 0 || unit(generator) < std::exp(-delta / temperature)) {
                current = proposal;
                current_score = proposal_score;
            }
            if (current_score < global_score) {
                global = current;
                global_score = current_score;
                if (global_score.excess == 0) {
                    global_score = evaluate(global, a, true);
                }
                print(global, global_score);
                if (global_score.excess == 0 && global_score.undecodable == 0) return 0;
            }
        }
    }
    print(global, global_score);
    return 2;
}
