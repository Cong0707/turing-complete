#include <algorithm>
#include <array>
#include <bit>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <random>
#include <regex>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>

// Constant-memory search for a zero-initialized, constant-seed 65-cycle RNG
// encoding that passes the delay-9 XOR2 Kraft necessary conditions.

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
    Matrix c{};
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

// T' = E*T for E = I + e_dst*e_src^T.  Since E is self-inverse,
// applying this mutation twice restores the exact previous state.
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
    int squared_excess = 0;
    int excess = 0;
    int violating_rows = 0;
    int maximum_load = 0;
    int total_load = 0;
    int total_weight = 0;

    auto key() const {
        return std::tie(
            squared_excess, excess, violating_rows, maximum_load,
            total_load, total_weight
        );
    }
};

Score score(const State& state) {
    Score result{};
    auto add = [&](int q_weight, int seed_weight) {
        const int load = 4 * q_weight + seed_weight;
        const int excess = std::max(0, load - 16);
        result.squared_excess += excess * excess;
        result.excess += excess;
        result.violating_rows += excess != 0;
        result.maximum_load = std::max(result.maximum_load, load);
        result.total_load += load;
        result.total_weight += q_weight + seed_weight;
    };
    for (int i = 0; i < N; ++i) {
        add(std::popcount(state.b[i]), std::popcount(state.d[i]));
        add(std::popcount(state.c[i]), std::popcount(A[i]));
    }
    return result;
}

std::int64_t scalar_energy(const Score& value) {
    return 100000000LL * value.squared_excess
         + 1000000LL * value.excess
         + 10000LL * value.violating_rows
         + 100LL * value.maximum_load
         + value.total_load;
}

void write_checkpoint(
    const std::string& path,
    const State& state,
    const Score& value,
    std::uint64_t seed,
    std::uint64_t step
) {
    const std::string temporary = path + ".tmp";
    std::ofstream out(temporary, std::ios::trunc);
    out << "{\n  \"schema\": 1,\n  \"model\": \"constant-seed delay9 XOR2 Kraft necessary condition\",\n";
    out << "  \"seed\": " << seed << ",\n  \"step\": " << step << ",\n";
    out << "  \"score\": {\"squared_excess\": " << value.squared_excess
        << ", \"excess\": " << value.excess
        << ", \"violating_rows\": " << value.violating_rows
        << ", \"maximum_load\": " << value.maximum_load
        << ", \"total_load\": " << value.total_load
        << ", \"total_weight\": " << value.total_weight << "},\n";
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
    std::cout << label << " step=" << step
              << " sq=" << value.squared_excess
              << " excess=" << value.excess
              << " bad=" << value.violating_rows
              << " max=" << value.maximum_load
              << " load=" << value.total_load
              << " weight=" << value.total_weight << '\n' << std::flush;
}

Matrix read_checkpoint_t(const std::string& path) {
    std::ifstream input(path);
    if (!input) throw std::runtime_error("cannot read input checkpoint");
    const std::string text(
        (std::istreambuf_iterator<char>(input)), std::istreambuf_iterator<char>()
    );
    const auto marker = text.find("\"T\"");
    if (marker == std::string::npos) throw std::runtime_error("checkpoint has no T array");
    const std::regex row_pattern("\"([0-9a-fA-F]{8})\"");
    Matrix result{};
    int count = 0;
    for (
        auto match = std::sregex_iterator(text.begin() + marker, text.end(), row_pattern);
        match != std::sregex_iterator() && count < N;
        ++match
    ) {
        result[count++] = static_cast<std::uint32_t>(std::stoul((*match)[1].str(), nullptr, 16));
    }
    if (count != N) throw std::runtime_error("checkpoint T array does not contain 32 rows");
    return result;
}

}  // namespace

int main(int argc, char** argv) {
    std::uint64_t seed = 0x65D09ULL;
    std::uint64_t steps_per_cycle = 5'000'000;
    int cycles = 20;
    std::string output = "kraft-frontier.json";
    std::string input;
    for (int i = 1; i < argc; ++i) {
        const std::string argument = argv[i];
        auto next = [&]() -> std::string {
            if (++i >= argc) throw std::runtime_error("missing argument value");
            return argv[i];
        };
        if (argument == "--seed") seed = std::stoull(next(), nullptr, 0);
        else if (argument == "--steps") steps_per_cycle = std::stoull(next(), nullptr, 0);
        else if (argument == "--cycles") cycles = std::stoi(next());
        else if (argument == "--output") output = next();
        else if (argument == "--input") input = next();
        else throw std::runtime_error("unknown argument: " + argument);
    }

    const Matrix fixed_t = multiply(right_shear(17), right_shear(13));
    const std::array<State, 3> starts = {
        from_t(identity()), from_t(right_shear(17)), from_t(fixed_t)
    };
    State best = input.empty()
        ? *std::min_element(starts.begin(), starts.end(), [](const State& x, const State& y) {
              return score(x).key() < score(y).key();
          })
        : from_t(read_checkpoint_t(input));
    Score best_score = score(best);
    write_checkpoint(output, best, best_score, seed, 0);
    print_score("initial", best_score, 0);

    std::uint64_t global_step = 0;
    for (int cycle = 0; cycle < cycles; ++cycle) {
        std::mt19937_64 rng(seed + static_cast<std::uint64_t>(cycle));
        std::uniform_real_distribution<double> unit(0.0, 1.0);
        State current = (input.empty() && cycle % 7 == 0) ? starts[cycle % starts.size()] : best;
        for (int perturb = 0; perturb < 3 + cycle % 47; ++perturb) {
            const int dst = static_cast<int>(rng() % N);
            int src = static_cast<int>(rng() % (N - 1));
            if (src >= dst) ++src;
            mutate(current, dst, src);
        }
        auto current_score = score(current);
        auto current_energy = scalar_energy(current_score);

        for (std::uint64_t step = 0; step < steps_per_cycle; ++step, ++global_step) {
            const int dst = static_cast<int>(rng() % N);
            int src = static_cast<int>(rng() % (N - 1));
            if (src >= dst) ++src;
            mutate(current, dst, src);
            const auto candidate_score = score(current);
            const auto candidate_energy = scalar_energy(candidate_score);
            const auto delta = candidate_energy - current_energy;
            const double fraction = static_cast<double>(step) /
                                    static_cast<double>(std::max<std::uint64_t>(1, steps_per_cycle));
            const double temperature = 5.0e9 * std::pow(1.0e-7, fraction) + 1.0;
            if (delta <= 0 || unit(rng) < std::exp(-static_cast<double>(delta) / temperature)) {
                current_score = candidate_score;
                current_energy = candidate_energy;
            } else {
                mutate(current, dst, src);
            }

            if ((step & 1023U) == 0 && current_score.key() < best_score.key()) {
                best = current;
                best_score = current_score;
                write_checkpoint(output, best, best_score, seed, global_step);
                print_score("best", best_score, global_step);
                if (best_score.squared_excess == 0) return 0;
            }
        }
        print_score("cycle", best_score, global_step);
    }
    return 1;
}
