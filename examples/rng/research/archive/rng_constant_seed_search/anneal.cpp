#include <algorithm>
#include <array>
#include <bit>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <random>
#include <string>
#include <tuple>

// Constant-memory GF(2) annealer for the always-available RNG seed model.
// It only writes a small research JSON checkpoint supplied on the command
// line; it has no save-game code.

namespace {

constexpr int N = 32;
using Matrix = std::array<std::uint32_t, N>;

std::uint32_t xorshift32(std::uint32_t value) {
    value ^= value >> 13;
    value ^= value << 17;
    value ^= value >> 5;
    return value;
}

Matrix identity() {
    Matrix result{};
    for (int i = 0; i < N; ++i) result[i] = std::uint32_t{1} << i;
    return result;
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

std::uint32_t apply_row(std::uint32_t row, const Matrix& right) {
    std::uint32_t result = 0;
    while (row) {
        const auto bit = row & (0U - row);
        result ^= right[std::countr_zero(bit)];
        row ^= bit;
    }
    return result;
}

Matrix multiply(const Matrix& left, const Matrix& right) {
    Matrix result{};
    for (int i = 0; i < N; ++i) result[i] = apply_row(left[i], right);
    return result;
}

Matrix inverse(Matrix work) {
    Matrix result = identity();
    for (int column = 0; column < N; ++column) {
        int pivot = column;
        while (pivot < N && !((work[pivot] >> column) & 1U)) ++pivot;
        if (pivot == N) throw std::runtime_error("singular matrix");
        std::swap(work[column], work[pivot]);
        std::swap(result[column], result[pivot]);
        for (int row = 0; row < N; ++row) {
            if (row != column && ((work[row] >> column) & 1U)) {
                work[row] ^= work[column];
                result[row] ^= result[column];
            }
        }
    }
    return result;
}

const Matrix A = natural_matrix();

Matrix a_plus_i() {
    Matrix result = A;
    for (int i = 0; i < N; ++i) result[i] ^= std::uint32_t{1} << i;
    return result;
}

const Matrix API = a_plus_i();

Matrix right_shear(int distance) {
    Matrix result{};
    for (int i = 0; i < N; ++i) {
        result[i] = std::uint32_t{1} << i;
        if (i + distance < N) result[i] |= std::uint32_t{1} << (i + distance);
    }
    return result;
}

struct State {
    Matrix t{};
    Matrix r{};
    Matrix b{};
    Matrix d{};
    Matrix c{};  // A*R, used by the direct-output objective.
};

State from_t(const Matrix& t) {
    State result{};
    result.t = t;
    result.r = inverse(t);
    result.b = multiply(multiply(t, A), result.r);
    result.d = multiply(t, API);
    result.c = multiply(A, result.r);
    return result;
}

void mutate(State& state, int dst, int src) {
    const auto dst_bit = std::uint32_t{1} << dst;
    const auto src_bit = std::uint32_t{1} << src;
    state.t[dst] ^= state.t[src];
    for (int i = 0; i < N; ++i) {
        if (state.r[i] & dst_bit) state.r[i] ^= src_bit;
        if (state.b[i] & dst_bit) state.b[i] ^= src_bit;
        if (state.c[i] & dst_bit) state.c[i] ^= src_bit;
    }
    state.b[dst] ^= state.b[src];
    state.d[dst] ^= state.d[src];
}

struct Score {
    int excess = 0;
    int heavy = 0;
    int maximum = 0;
    int total = 0;

    auto key() const { return std::tie(excess, heavy, maximum, total); }
};

enum class Mode { Cascade2, Direct3 };

Score score(const State& state, Mode mode) {
    const int limit = mode == Mode::Cascade2 ? 4 : 8;
    Score result{};
    auto add = [&](int weight) {
        result.total += weight;
        result.maximum = std::max(result.maximum, weight);
        if (weight > limit) {
            ++result.heavy;
            const int delta = weight - limit;
            result.excess += delta * delta;
        }
    };
    for (int i = 0; i < N; ++i) {
        add(std::popcount(state.b[i]) + std::popcount(state.d[i]));
    }
    for (int i = 0; i < N; ++i) {
        if (mode == Mode::Cascade2) {
            add(std::popcount(state.r[i]) + 1);
        } else {
            add(std::popcount(state.c[i]) + std::popcount(A[i]));
        }
    }
    return result;
}

std::int64_t energy(const Score& value) {
    if (value.excess) {
        return 20'000'000LL + 1'000'000LL * value.excess +
               50'000LL * value.heavy + 2'000LL * value.maximum + value.total;
    }
    return value.total;
}

bool decoder_within(const State& state, int maximum) {
    if (maximum < 0) return true;
    return std::all_of(state.r.begin(), state.r.end(), [&](std::uint32_t row) {
        return std::popcount(row) <= maximum;
    });
}

void write_checkpoint(
    const std::string& path,
    const State& state,
    const Score& value,
    Mode mode,
    std::uint64_t seed,
    std::uint64_t step
) {
    const std::string temporary = path + ".tmp";
    std::ofstream out(temporary, std::ios::trunc);
    out << "{\n  \"mode\": \""
        << (mode == Mode::Cascade2 ? "cascade2" : "direct3") << "\",\n";
    out << "  \"seed\": " << seed << ",\n  \"step\": " << step << ",\n";
    out << "  \"score\": {\"quadratic_excess\": " << value.excess
        << ", \"heavy_rows\": " << value.heavy
        << ", \"maximum_weight\": " << value.maximum
        << ", \"total_weight\": " << value.total << "},\n";
    out << "  \"T\": [\n";
    for (int i = 0; i < N; ++i) {
        out << "    \"" << std::hex << std::setfill('0') << std::setw(8) << state.t[i]
            << "\"" << (i + 1 == N ? "\n" : ",\n");
    }
    out << "  ]\n}\n";
    out.close();
    std::remove(path.c_str());
    if (std::rename(temporary.c_str(), path.c_str()) != 0) {
        throw std::runtime_error("cannot replace checkpoint");
    }
}

void print_score(const char* label, const Score& value, std::uint64_t step) {
    std::cout << label << " step=" << step << " excess=" << value.excess
              << " heavy=" << value.heavy << " max=" << value.maximum
              << " total=" << value.total << '\n' << std::flush;
}

}  // namespace

int main(int argc, char** argv) {
    std::uint64_t seed = 0xC057A17ULL;
    std::uint64_t steps_per_cycle = 5'000'000;
    int cycles = 20;
    int decoder_maximum = -1;
    Mode mode = Mode::Cascade2;
    std::string output = "frontier-cpp.json";
    for (int i = 1; i < argc; ++i) {
        const std::string argument = argv[i];
        auto next = [&]() -> std::string {
            if (++i >= argc) throw std::runtime_error("missing argument value");
            return argv[i];
        };
        if (argument == "--seed") seed = std::stoull(next(), nullptr, 0);
        else if (argument == "--steps") steps_per_cycle = std::stoull(next(), nullptr, 0);
        else if (argument == "--cycles") cycles = std::stoi(next());
        else if (argument == "--decoder-max-weight") decoder_maximum = std::stoi(next());
        else if (argument == "--mode") {
            const auto value = next();
            if (value == "cascade2") mode = Mode::Cascade2;
            else if (value == "direct3") mode = Mode::Direct3;
            else throw std::runtime_error("mode must be cascade2 or direct3");
        } else if (argument == "--output") output = next();
        else throw std::runtime_error("unknown argument: " + argument);
    }

    const Matrix single_shear_t = right_shear(17);
    const Matrix fixed_t = multiply(single_shear_t, right_shear(13));
    const std::array<State, 3> starts = {
        from_t(identity()), from_t(single_shear_t), from_t(fixed_t)
    };
    State best = starts[0];
    Score best_score = score(best, mode);
    for (const auto& item : starts) {
        const auto item_score = score(item, mode);
        if (decoder_within(item, decoder_maximum) && item_score.key() < best_score.key()) {
            best = item;
            best_score = item_score;
        }
    }
    if (!decoder_within(best, decoder_maximum)) {
        throw std::runtime_error("no built-in start satisfies decoder limit");
    }
    write_checkpoint(output, best, best_score, mode, seed, 0);
    print_score("initial", best_score, 0);

    std::uint64_t global_step = 0;
    for (int cycle = 0; cycle < cycles; ++cycle) {
        std::mt19937_64 rng(seed + static_cast<std::uint64_t>(cycle));
        std::uniform_real_distribution<double> unit(0.0, 1.0);
        State current = (cycle % 7 == 0 && decoder_within(starts[0], decoder_maximum))
                            ? starts[0]
                            : best;
        for (int perturb = 0; perturb < 3 + cycle % 47; ++perturb) {
            for (int attempts = 0; attempts < 256; ++attempts) {
                const int dst = static_cast<int>(rng() % N);
                int src = static_cast<int>(rng() % (N - 1));
                if (src >= dst) ++src;
                mutate(current, dst, src);
                if (decoder_within(current, decoder_maximum)) break;
                mutate(current, dst, src);
            }
        }
        auto current_score = score(current, mode);
        auto current_energy = energy(current_score);

        for (std::uint64_t step = 0; step < steps_per_cycle; ++step, ++global_step) {
            const int dst = static_cast<int>(rng() % N);
            int src = static_cast<int>(rng() % (N - 1));
            if (src >= dst) ++src;
            mutate(current, dst, src);
            if (!decoder_within(current, decoder_maximum)) {
                mutate(current, dst, src);
                continue;
            }
            const auto candidate_score = score(current, mode);
            const auto candidate_energy = energy(candidate_score);
            const auto delta = candidate_energy - current_energy;
            const double fraction = static_cast<double>(step) /
                                    static_cast<double>(std::max<std::uint64_t>(1, steps_per_cycle));
            const double temperature = 8'000'000.0 * std::pow(0.000001, fraction) + 1.0;
            if (delta <= 0 || unit(rng) < std::exp(-static_cast<double>(delta) / temperature)) {
                current_score = candidate_score;
                current_energy = candidate_energy;
            } else {
                mutate(current, dst, src);
            }

            if ((step & 1023U) == 0 && current_score.key() < best_score.key()) {
                best = current;
                best_score = current_score;
                write_checkpoint(output, best, best_score, mode, seed, global_step);
                print_score("best", best_score, global_step);
                if (best_score.excess == 0) return 0;
            }
        }
        print_score("cycle", best_score, global_step);
    }
    return 0;
}
