#include <algorithm>
#include <array>
#include <bit>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <random>
#include <set>
#include <tuple>
#include <vector>

using Matrix = std::array<std::uint32_t, 32>;

namespace {

constexpr int N = 32;

std::uint32_t xorshift32(std::uint32_t value) {
    value ^= value >> 13;
    value ^= value << 17;
    value ^= value >> 5;
    return value;
}

Matrix transition_matrix() {
    Matrix rows{};
    for (int source = 0; source < N; ++source) {
        const auto output = xorshift32(std::uint32_t{1} << source);
        for (int target = 0; target < N; ++target) {
            rows[target] |= ((output >> target) & 1U) << source;
        }
    }
    return rows;
}

struct State {
    Matrix T{};
    Matrix B{};
    Matrix C{};
};

State identity_state() {
    State state;
    state.B = transition_matrix();
    state.C = state.B;
    for (int bit = 0; bit < N; ++bit) {
        state.T[bit] = std::uint32_t{1} << bit;
    }
    return state;
}

// T' = E*T, B' = E*B*E, C' = C*E for E = I + e_dst e_src^T.
void shear(State& state, int dst, int src) {
    const auto dst_bit = std::uint32_t{1} << dst;
    const auto src_bit = std::uint32_t{1} << src;
    state.T[dst] ^= state.T[src];
    for (auto& row : state.B) {
        if (row & dst_bit) row ^= src_bit;
    }
    state.B[dst] ^= state.B[src];
    for (auto& row : state.C) {
        if (row & dst_bit) row ^= src_bit;
    }
}

struct Score {
    int excess = 0;
    int heavy = 0;
    int maximum = 0;
    int weight = 0;
    int init_xor = 0;
    int greedy_xor = 1000;

    auto key() const {
        return std::tuple(excess, heavy, maximum, greedy_xor + init_xor,
                          greedy_xor, init_xor, weight);
    }
};

std::vector<std::uint32_t> pairs(std::uint32_t row) {
    std::vector<std::uint32_t> bits;
    while (row) {
        const auto bit = row & (~row + 1);
        bits.push_back(bit);
        row ^= bit;
    }
    std::vector<std::uint32_t> result;
    for (std::size_t i = 0; i < bits.size(); ++i) {
        for (std::size_t j = i + 1; j < bits.size(); ++j) {
            result.push_back(bits[i] | bits[j]);
        }
    }
    return result;
}

bool satisfied(std::uint32_t row, const std::set<std::uint32_t>& selected) {
    const int weight = std::popcount(row);
    if (weight == 3) {
        for (auto pair : pairs(row)) if (selected.contains(pair)) return true;
        return false;
    }
    if (weight == 4) {
        for (auto pair : pairs(row)) {
            const auto other = row ^ pair;
            if (std::popcount(other) == 2 && selected.contains(pair) && selected.contains(other)) {
                return true;
            }
        }
        return false;
    }
    return weight <= 2;
}

int greedy_depth_two(const State& state) {
    std::set<std::uint32_t> targets;
    for (const auto& matrix : {state.B, state.C}) {
        targets.insert(matrix.begin(), matrix.end());
    }
    std::set<std::uint32_t> selected;
    int finals = 0;
    for (auto row : targets) {
        const int weight = std::popcount(row);
        if (weight == 0 || weight > 4) return 1000;
        if (weight == 2) selected.insert(row);
        if (weight >= 3) ++finals;
    }
    while (true) {
        std::vector<std::uint32_t> unmet;
        for (auto row : targets) {
            if (std::popcount(row) >= 3 && !satisfied(row, selected)) unmet.push_back(row);
        }
        if (unmet.empty()) break;

        std::set<std::vector<std::uint32_t>> actions;
        for (auto row : unmet) {
            const auto row_pairs = pairs(row);
            if (std::popcount(row) == 3) {
                for (auto pair : row_pairs) {
                    if (!selected.contains(pair)) actions.insert({pair});
                }
            } else {
                for (auto pair : row_pairs) {
                    const auto other = row ^ pair;
                    if (std::popcount(other) != 2 || pair > other) continue;
                    std::vector<std::uint32_t> action;
                    if (!selected.contains(pair)) action.push_back(pair);
                    if (!selected.contains(other)) action.push_back(other);
                    if (!action.empty()) actions.insert(action);
                }
            }
        }
        std::vector<std::uint32_t> best;
        auto best_key = std::tuple(-1.0, -1, 0, std::vector<std::uint32_t>{});
        for (const auto& action : actions) {
            auto trial = selected;
            trial.insert(action.begin(), action.end());
            int gain = 0;
            for (auto row : unmet) gain += satisfied(row, trial);
            auto key = std::tuple(double(gain) / action.size(), gain,
                                  -int(action.size()), action);
            if (key > best_key) {
                best_key = key;
                best = action;
            }
        }
        if (best.empty()) return 1000;
        selected.insert(best.begin(), best.end());
    }
    return int(selected.size()) + finals;
}

Score score(const State& state) {
    Score result;
    for (auto row : state.T) result.init_xor += std::popcount(row) == 2;
    for (const auto& matrix : {state.B, state.C}) {
        for (auto row : matrix) {
            const int weight = std::popcount(row);
            result.maximum = std::max(result.maximum, weight);
            result.weight += weight;
            if (weight > 4) {
                ++result.heavy;
                const int e = weight - 4;
                result.excess += e * e;
            }
        }
    }
    if (result.excess == 0) result.greedy_xor = greedy_depth_two(state);
    return result;
}

double energy(const Score& s) {
    if (s.excess) {
        return 1e8 * s.excess + 1e6 * s.heavy + 1e4 * s.maximum + s.weight;
    }
    return 1e5 * (s.greedy_xor + s.init_xor) + 1e3 * s.greedy_xor + s.weight;
}

void print_candidate(std::uint64_t step, const State& state, const Score& s) {
    std::printf("{\"step\":%llu,\"score\":{\"excess\":%d,\"heavy\":%d,"
                "\"maximum\":%d,\"weight\":%d,\"init_xor\":%d,"
                "\"greedy_xor\":%d,\"xor_total\":%d},\"T\":[",
                static_cast<unsigned long long>(step), s.excess, s.heavy, s.maximum,
                s.weight, s.init_xor, s.greedy_xor, s.init_xor + s.greedy_xor);
    for (int i = 0; i < N; ++i) std::printf("%s\"%08x\"", i ? "," : "", state.T[i]);
    std::printf("],\"B\":[");
    for (int i = 0; i < N; ++i) std::printf("%s\"%08x\"", i ? "," : "", state.B[i]);
    std::printf("],\"C\":[");
    for (int i = 0; i < N; ++i) std::printf("%s\"%08x\"", i ? "," : "", state.C[i]);
    std::printf("]}\n");
    std::fflush(stdout);
}

}  // namespace

int main(int argc, char** argv) {
    const std::uint64_t seed = argc > 1 ? std::strtoull(argv[1], nullptr, 0) : 0x9901;
    const std::uint64_t steps = argc > 2 ? std::strtoull(argv[2], nullptr, 0) : 20000000;
    std::mt19937_64 rng(seed);
    State state = identity_state();
    Score current_score = score(state);
    State best = state;
    Score best_score = current_score;
    print_candidate(0, best, best_score);

    for (std::uint64_t step = 1; step <= steps; ++step) {
        const int dst = int(rng() % N);
        int src = int(rng() % (N - 1));
        src += src >= dst;
        const auto new_row = state.T[dst] ^ state.T[src];
        if (new_row == 0 || std::popcount(new_row) > 2) continue;

        const auto old_energy = energy(current_score);
        shear(state, dst, src);
        const auto candidate_score = score(state);
        const auto candidate_energy = energy(candidate_score);
        const double phase = double(step % 200000) / 200000.0;
        const double temperature = 5e8 * std::pow(1e-5, phase) + 1.0;
        const double delta = candidate_energy - old_energy;
        const double unit = double(rng() >> 11) * (1.0 / 9007199254740992.0);
        if (delta <= 0 || unit < std::exp(-delta / temperature)) {
            current_score = candidate_score;
        } else {
            shear(state, dst, src);
        }

        if (current_score.key() < best_score.key()) {
            best = state;
            best_score = current_score;
            print_candidate(step, best, best_score);
            std::fprintf(stderr,
                         "best step=%llu excess=%d heavy=%d max=%d steady=%d init=%d total=%d\n",
                         static_cast<unsigned long long>(step), best_score.excess,
                         best_score.heavy, best_score.maximum, best_score.greedy_xor,
                         best_score.init_xor, best_score.greedy_xor + best_score.init_xor);
        }

        // Periodic restart from the best sparse basis avoids long random drift.
        if (step % 200000 == 0) {
            state = best;
            current_score = best_score;
        }
    }
    return 0;
}
