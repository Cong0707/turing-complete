#include <algorithm>
#include <array>
#include <bit>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <random>
#include <tuple>

using Rows32 = std::array<std::uint32_t, 32>;
using Basis10 = std::array<std::uint32_t, 10>;

static std::uint32_t xorshift32(std::uint32_t value) {
    value ^= value >> 13;
    value ^= value << 17;
    value ^= value >> 5;
    return value;
}

static Rows32 matrix_from_xorshift() {
    Rows32 rows{};
    for (int source = 0; source < 32; ++source) {
        const auto output = xorshift32(std::uint32_t{1} << source);
        for (int target = 0; target < 32; ++target) {
            rows[target] |= ((output >> target) & 1U) << source;
        }
    }
    return rows;
}

static std::uint32_t apply_row(std::uint32_t row, const Rows32& matrix) {
    std::uint32_t result = 0;
    while (row) {
        const auto bit = std::countr_zero(row);
        result ^= matrix[bit];
        row &= row - 1;
    }
    return result;
}

static Basis10 initial_basis() {
    std::array<std::uint32_t, 32> a{};
    std::array<std::uint32_t, 32> b{};
    for (int bit = 0; bit < 32; ++bit) {
        a[bit] = std::uint32_t{1} << bit;
        if (bit + 13 < 32) a[bit] ^= std::uint32_t{1} << (bit + 13);
    }
    for (int bit = 0; bit < 32; ++bit) {
        b[bit] = a[bit];
        if (bit >= 17) b[bit] ^= a[bit - 17];
    }
    Basis10 basis{};
    std::copy_n(b.begin() + 17, 10, basis.begin());
    return basis;
}

struct Evaluation {
    int heavy = 0;
    int excess = 0;
    int maximum = 0;
    int total = 0;
    std::array<std::uint64_t, 42> representatives{};

    auto key() const { return std::tuple(heavy, excess, maximum, total); }
    int energy() const { return heavy * 100000 + excess * 10000 + maximum * 1000 + total; }
};

static int rank(Basis10 rows) {
    int result = 0;
    for (int column = 31; column >= 0; --column) {
        int pivot = result;
        while (pivot < 10 && ((rows[pivot] >> column) & 1U) == 0) ++pivot;
        if (pivot == 10) continue;
        std::swap(rows[result], rows[pivot]);
        for (int row = 0; row < 10; ++row) {
            if (row != result && ((rows[row] >> column) & 1U)) rows[row] ^= rows[result];
        }
        ++result;
    }
    return result;
}

static Evaluation evaluate(const Basis10& basis, const Rows32& A) {
    std::array<std::uint32_t, 1024> span{};
    std::array<int, 1024> coefficient_weight{};
    for (int mask = 1; mask < 1024; ++mask) {
        const int bit = std::countr_zero(static_cast<unsigned>(mask));
        const int previous = mask & (mask - 1);
        span[mask] = span[previous] ^ basis[bit];
        coefficient_weight[mask] = coefficient_weight[previous] + 1;
    }

    std::array<std::uint32_t, 42> targets{};
    std::copy(A.begin(), A.end(), targets.begin());
    for (int index = 0; index < 10; ++index) {
        targets[32 + index] = apply_row(basis[index], A);
    }

    Evaluation result;
    for (int index = 0; index < 42; ++index) {
        int best_weight = 100;
        int best_mask = 0;
        std::uint32_t best_base = 0;
        for (int mask = 0; mask < 1024; ++mask) {
            const std::uint32_t base = targets[index] ^ span[mask];
            const int weight = std::popcount(base) + coefficient_weight[mask];
            if (weight < best_weight) {
                best_weight = weight;
                best_mask = mask;
                best_base = base;
            }
        }
        result.heavy += best_weight > 4;
        if (best_weight > 4) result.excess += (best_weight - 4) * (best_weight - 4);
        result.maximum = std::max(result.maximum, best_weight);
        result.total += best_weight;
        result.representatives[index] =
            static_cast<std::uint64_t>(best_base) |
            (static_cast<std::uint64_t>(best_mask) << 32);
    }
    return result;
}

static void print_candidate(const Basis10& basis, const Evaluation& evaluation) {
    std::printf("score heavy=%d excess=%d max=%d total=%d\n",
                evaluation.heavy, evaluation.excess,
                evaluation.maximum, evaluation.total);
    std::puts("H");
    for (const auto row : basis) std::printf("%08x\n", row);
    std::puts("F");
    for (const auto row : evaluation.representatives) {
        std::printf("%011llx\n", static_cast<unsigned long long>(row));
    }
    std::fflush(stdout);
}

int main(int argc, char** argv) {
    const std::uint64_t seed = argc > 1 ? std::strtoull(argv[1], nullptr, 0) : 20260801;
    const std::uint64_t steps = argc > 2 ? std::strtoull(argv[2], nullptr, 0) : 50000000;
    const Rows32 A = matrix_from_xorshift();
    Basis10 current = initial_basis();
    Evaluation current_score = evaluate(current, A);
    Basis10 best = current;
    Evaluation best_score = current_score;
    print_candidate(best, best_score);

    std::mt19937_64 rng(seed);
    for (std::uint64_t step = 0; step < steps; ++step) {
        Basis10 next = current;
        const int destination = static_cast<int>(rng() % 10);
        if ((rng() & 3U) == 0) {
            int source = static_cast<int>(rng() % 9);
            if (source >= destination) ++source;
            next[destination] ^= next[source];
        } else {
            next[destination] ^= std::uint32_t{1} << (rng() % 32);
            if (rank(next) != 10) continue;
        }
        const Evaluation score = evaluate(next, A);

        const double phase = static_cast<double>(step % 200000) / 200000.0;
        const double temperature = 5000.0 * (1.0 - phase) + 10.0;
        const int delta = score.energy() - current_score.energy();
        bool accept = delta <= 0;
        if (!accept) {
            const double draw = static_cast<double>(rng() >> 11) * (1.0 / 9007199254740992.0);
            accept = draw < std::exp(-static_cast<double>(delta) / temperature);
        }
        if (accept) {
            current = next;
            current_score = score;
        }
        if (score.key() < best_score.key()) {
            best = next;
            best_score = score;
            print_candidate(best, best_score);
            if (best_score.heavy == 0) return 0;
        }
        if ((step + 1) % 1000000 == 0) {
            current = best;
            current_score = best_score;
        }
    }
    return best_score.heavy == 0 ? 0 : 2;
}
