#include <algorithm>
#include <array>
#include <bit>
#include <chrono>
#include <cstdint>
#include <cstdlib>
#include <fstream>
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

// Research-only, single-process search.  Matrices are GF(2) row matrices.
// For q = P*A*x:
//   B = P*A*P^-1  (registered feedback)
//   C = P^-1      (visible x_next)
// A k-step row-XOR program realizes P in at most k XOR2 gates before the
// phase switch.  B and C are synthesized as one shared depth-two network.

namespace {

constexpr int N = 32;
using Matrix = std::array<std::uint32_t, N>;

struct Op {
    std::uint8_t dst;
    std::uint8_t src;
};

struct Candidate {
    std::vector<Op> ops;
    std::array<std::uint8_t, N> permutation{};
    Matrix p{};
    Matrix b{};
    Matrix c{};
};

struct Score {
    int maximum_weight = 0;
    int heavy_rows = 0;
    int excess = 0;
    int distinct_nonunit = 0;
    int total_weight = 0;
    int greedy_depth2 = 1000000;
    int total_upper = 1000000;
    std::int64_t energy = 0;

    auto key() const {
        return std::tie(maximum_weight, heavy_rows, excess, total_upper,
                        distinct_nonunit, total_weight);
    }
};

std::uint32_t xorshift32(std::uint32_t value) {
    value ^= value >> 13;
    value ^= value << 17;
    value ^= value >> 5;
    return value;
}

Matrix natural_matrix() {
    Matrix result{};
    for (int source = 0; source < N; ++source) {
        const auto output = xorshift32(std::uint32_t{1} << source);
        for (int target = 0; target < N; ++target) {
            if ((output >> target) & 1U) result[target] |= std::uint32_t{1} << source;
        }
    }
    return result;
}

void mutate(Matrix& p, Matrix& b, Matrix& c, Op op) {
    const auto dst_bit = std::uint32_t{1} << op.dst;
    const auto src_bit = std::uint32_t{1} << op.src;
    p[op.dst] ^= p[op.src];
    for (auto& row : b) {
        if (row & dst_bit) row ^= src_bit;
    }
    b[op.dst] ^= b[op.src];
    for (auto& row : c) {
        if (row & dst_bit) row ^= src_bit;
    }
}

Matrix multiply(const Matrix& left, const Matrix& right) {
    Matrix result{};
    for (int i = 0; i < N; ++i) {
        auto remaining = left[i];
        while (remaining) {
            const auto bit = remaining & (~remaining + 1U);
            result[i] ^= right[std::countr_zero(bit)];
            remaining ^= bit;
        }
    }
    return result;
}

Candidate evaluate_ops(const std::vector<Op>& ops,
                       const std::array<std::uint8_t, N>& permutation) {
    Candidate result;
    result.ops = ops;
    result.permutation = permutation;
    Matrix permutation_matrix{};
    for (int i = 0; i < N; ++i) permutation_matrix[i] = std::uint32_t{1} << permutation[i];
    Matrix inverse_permutation{};
    for (int i = 0; i < N; ++i) inverse_permutation[permutation[i]] = std::uint32_t{1} << i;
    result.p = permutation_matrix;
    result.b = multiply(multiply(permutation_matrix, natural_matrix()), inverse_permutation);
    result.c = inverse_permutation;
    for (const auto op : ops) mutate(result.p, result.b, result.c, op);
    return result;
}

std::vector<std::array<std::uint32_t, 2>> options(std::uint32_t row) {
    std::vector<int> bits;
    for (int i = 0; i < N; ++i) if ((row >> i) & 1U) bits.push_back(i);
    std::vector<std::array<std::uint32_t, 2>> result;
    if (bits.size() == 3) {
        for (int lone : bits) {
            const auto unit = std::uint32_t{1} << lone;
            result.push_back({unit, row ^ unit});
        }
    } else if (bits.size() == 4) {
        const auto a = std::uint32_t{1} << bits[0];
        for (int j = 1; j < 4; ++j) {
            const auto pair = a | (std::uint32_t{1} << bits[j]);
            result.push_back({pair, row ^ pair});
        }
    }
    return result;
}

bool satisfied(std::uint32_t row, const std::unordered_set<std::uint32_t>& pairs) {
    for (const auto& option : options(row)) {
        const bool left = std::popcount(option[0]) == 1 || pairs.contains(option[0]);
        const bool right = std::popcount(option[1]) == 1 || pairs.contains(option[1]);
        if (left && right) return true;
    }
    return false;
}

int greedy_depth_two(const Matrix& b, const Matrix& c) {
    std::set<std::uint32_t> targets;
    targets.insert(b.begin(), b.end());
    targets.insert(c.begin(), c.end());
    std::unordered_set<std::uint32_t> pairs;
    std::vector<std::uint32_t> finals;
    for (auto row : targets) {
        const int weight = std::popcount(row);
        if (weight == 0 || weight > 4) return 1000000;
        if (weight == 2) pairs.insert(row);
        if (weight >= 3) finals.push_back(row);
    }
    while (true) {
        std::vector<std::uint32_t> unmet;
        for (auto row : finals) if (!satisfied(row, pairs)) unmet.push_back(row);
        if (unmet.empty()) break;
        std::set<std::vector<std::uint32_t>> actions;
        for (auto row : unmet) {
            for (const auto& option : options(row)) {
                std::vector<std::uint32_t> action;
                for (auto value : option) {
                    if (std::popcount(value) == 2 && !pairs.contains(value)) action.push_back(value);
                }
                std::sort(action.begin(), action.end());
                action.erase(std::unique(action.begin(), action.end()), action.end());
                if (!action.empty()) actions.insert(action);
            }
        }
        std::vector<std::uint32_t> best;
        std::tuple<double, int, int, std::vector<std::uint32_t>> best_key{-1.0, -1, -3, {}};
        for (const auto& action : actions) {
            auto trial = pairs;
            trial.insert(action.begin(), action.end());
            int gain = 0;
            for (auto row : unmet) gain += satisfied(row, trial);
            auto reverse = action;
            for (auto& value : reverse) value = ~value;
            const auto key = std::make_tuple(double(gain) / action.size(), gain,
                                             -int(action.size()), reverse);
            if (key > best_key) {
                best_key = key;
                best = action;
            }
        }
        if (best.empty()) return 1000000;
        pairs.insert(best.begin(), best.end());
    }
    bool changed = true;
    std::unordered_set<std::uint32_t> required;
    for (auto row : targets) if (std::popcount(row) == 2) required.insert(row);
    while (changed) {
        changed = false;
        std::vector<std::uint32_t> removable;
        for (auto pair : pairs) if (!required.contains(pair)) removable.push_back(pair);
        std::sort(removable.rbegin(), removable.rend());
        for (auto pair : removable) {
            auto trial = pairs;
            trial.erase(pair);
            bool ok = true;
            for (auto row : finals) ok &= satisfied(row, trial);
            if (ok) {
                pairs = std::move(trial);
                changed = true;
            }
        }
    }
    return int(pairs.size() + finals.size());
}

Score score(const Candidate& candidate) {
    Score result;
    std::set<std::uint32_t> nonunit;
    for (const auto* matrix : {&candidate.b, &candidate.c}) {
        for (auto row : *matrix) {
            const int weight = std::popcount(row);
            result.maximum_weight = std::max(result.maximum_weight, weight);
            result.heavy_rows += weight > 4;
            result.excess += std::max(0, weight - 4) * std::max(0, weight - 4);
            result.total_weight += weight;
            if (weight > 1) nonunit.insert(row);
        }
    }
    result.distinct_nonunit = int(nonunit.size());
    if (result.heavy_rows == 0) {
        result.greedy_depth2 = greedy_depth_two(candidate.b, candidate.c);
        result.total_upper = int(candidate.ops.size()) + result.greedy_depth2;
    }
    result.energy = 200000LL * result.heavy_rows + 100000LL * result.excess
        + 400000LL * std::max(0, result.maximum_weight - 5)
        + 800LL * result.distinct_nonunit + result.total_weight;
    if (result.heavy_rows == 0) result.energy += 1000LL * result.total_upper;
    return result;
}

void print_matrix(std::ostream& out, const char* label, const Matrix& matrix) {
    out << label << "\n";
    for (auto row : matrix) {
        out << std::hex << std::setfill('0') << std::setw(8) << row << "\n";
    }
    out << std::dec;
}

void write_candidate(const Candidate& candidate, const Score& value,
                     const std::string& path, std::uint64_t seed, long long step) {
    std::ofstream out(path);
    out << "seed " << seed << "\nstep " << step << "\n";
    out << "ops " << candidate.ops.size() << "\n";
    out << "permutation";
    for (auto value : candidate.permutation) out << " " << int(value);
    out << "\n";
    for (const auto op : candidate.ops) out << int(op.dst) << " " << int(op.src) << "\n";
    out << "score " << value.maximum_weight << " " << value.heavy_rows << " "
        << value.excess << " " << value.distinct_nonunit << " " << value.total_weight
        << " " << value.greedy_depth2 << " " << value.total_upper << "\n";
    print_matrix(out, "P", candidate.p);
    print_matrix(out, "B", candidate.b);
    print_matrix(out, "C", candidate.c);
}

Op random_op(std::mt19937_64& rng) {
    int dst = int(rng() % N);
    int src = int(rng() % (N - 1));
    if (src >= dst) ++src;
    return {std::uint8_t(dst), std::uint8_t(src)};
}

}  // namespace

int main(int argc, char** argv) {
    int length = argc > 1 ? std::atoi(argv[1]) : 16;
    long long steps = argc > 2 ? std::atoll(argv[2]) : 5000000;
    std::uint64_t seed = argc > 3 ? std::strtoull(argv[3], nullptr, 0) : 0xC0DEC0DEULL;
    std::string output = argc > 4 ? argv[4] : "short_basis_best.txt";
    std::mt19937_64 rng(seed);

    std::vector<Op> ops(length);
    for (auto& op : ops) op = random_op(rng);
    std::array<std::uint8_t, N> permutation{};
    for (int i = 0; i < N; ++i) permutation[i] = std::uint8_t(i);
    std::shuffle(permutation.begin(), permutation.end(), rng);
    Candidate current = evaluate_ops(ops, permutation);
    Score current_score = score(current);
    Candidate best = current;
    Score best_score = current_score;
    auto started = std::chrono::steady_clock::now();

    for (long long step = 0; step < steps; ++step) {
        const bool change_permutation = (rng() & 3U) == 0;
        const int slot = int(rng() % ops.size());
        const Op old = ops[slot];
        int first = int(rng() % N);
        int second = int(rng() % (N - 1));
        if (second >= first) ++second;
        if (change_permutation) std::swap(permutation[first], permutation[second]);
        else ops[slot] = random_op(rng);
        Candidate trial = evaluate_ops(ops, permutation);
        Score trial_score = score(trial);
        const auto delta = double(trial_score.energy - current_score.energy);
        const double phase = double(step % 200000) / 200000.0;
        const double temperature = 120000.0 * std::pow(0.00001, phase) + 2.0;
        const double random_unit = double(rng() >> 11) * (1.0 / 9007199254740992.0);
        if (delta <= 0 || random_unit < std::exp(-delta / temperature)) {
            current = std::move(trial);
            current_score = trial_score;
        } else {
            if (change_permutation) std::swap(permutation[first], permutation[second]);
            else ops[slot] = old;
        }

        if (current_score.key() < best_score.key()) {
            best = current;
            best_score = current_score;
            write_candidate(best, best_score, output, seed, step);
            std::cerr << "best step=" << step << " max=" << best_score.maximum_weight
                      << " heavy=" << best_score.heavy_rows
                      << " distinct=" << best_score.distinct_nonunit
                      << " depth2=" << best_score.greedy_depth2
                      << " total=" << best_score.total_upper << "\n";
        }

        // Deterministic reheating restart, retaining a little structure from best.
        if (step && step % 200000 == 0 && best_score.heavy_rows != 0) {
            ops = best.ops;
            permutation = best.permutation;
            for (int i = 0; i < std::max(1, length / 4); ++i) ops[rng() % ops.size()] = random_op(rng);
            for (int i = 0; i < 2; ++i) {
                const int a = int(rng() % N);
                int b = int(rng() % (N - 1));
                if (b >= a) ++b;
                std::swap(permutation[a], permutation[b]);
            }
            current = evaluate_ops(ops, permutation);
            current_score = score(current);
        }
    }
    write_candidate(best, best_score, output, seed, steps);
    const auto elapsed = std::chrono::duration<double>(std::chrono::steady_clock::now() - started).count();
    std::cout << "length=" << length << " steps=" << steps << " elapsed=" << elapsed
              << " max=" << best_score.maximum_weight << " heavy=" << best_score.heavy_rows
              << " distinct=" << best_score.distinct_nonunit
              << " depth2=" << best_score.greedy_depth2
              << " total=" << best_score.total_upper << "\n";
}
