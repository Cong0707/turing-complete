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
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>

namespace {

constexpr int N = 32;
using Matrix = std::array<std::uint32_t, N>;

std::uint32_t xs(std::uint32_t value) {
    value ^= value >> 13;
    value ^= value << 17;
    value ^= value >> 5;
    return value;
}

Matrix transition() {
    Matrix result{};
    for (int source = 0; source < N; ++source) {
        const auto value = xs(std::uint32_t{1} << source);
        for (int target = 0; target < N; ++target) {
            result[target] |= ((value >> target) & 1U) << source;
        }
    }
    return result;
}

Matrix identity() {
    Matrix result{};
    for (int bit = 0; bit < N; ++bit) result[bit] = std::uint32_t{1} << bit;
    return result;
}

std::uint32_t apply_row(std::uint32_t row, const Matrix& matrix) {
    std::uint32_t result = 0;
    while (row) {
        const int bit = std::countr_zero(row);
        result ^= matrix[bit];
        row &= row - 1;
    }
    return result;
}

Matrix multiply(const Matrix& left, const Matrix& right) {
    Matrix result{};
    for (int row = 0; row < N; ++row) result[row] = apply_row(left[row], right);
    return result;
}

Matrix inverse(Matrix matrix) {
    Matrix result = identity();
    for (int column = 0; column < N; ++column) {
        int pivot = column;
        while (pivot < N && ((matrix[pivot] >> column) & 1U) == 0) ++pivot;
        if (pivot == N) throw std::runtime_error("singular C");
        std::swap(matrix[column], matrix[pivot]);
        std::swap(result[column], result[pivot]);
        for (int row = 0; row < N; ++row) {
            if (row != column && ((matrix[row] >> column) & 1U)) {
                matrix[row] ^= matrix[column];
                result[row] ^= result[column];
            }
        }
    }
    return result;
}

struct Score {
    int over = 0;
    int excess = 0;
    int maximum = 0;
    int combined_weight = 0;
    int b_weight = 0;
    int t_weight = 0;
    int c_weight = 0;

    auto key() const {
        return std::tuple(over, excess, maximum, combined_weight, b_weight, t_weight);
    }

    double energy() const {
        // A single very heavy row often has to split into several temporary
        // light violations before all of them can be repaired.
        return 1.5e5 * over + 2.0e4 * excess
             + 5.0e3 * std::max(0, maximum - 16)
             + 10.0 * combined_weight + c_weight;
    }
};

struct State {
    Matrix C{};
    Matrix P{};
    Matrix T{};
    Matrix B{};
    Score score{};
};

State make_state(const Matrix& c, const Matrix& a, const Matrix& a_plus_i) {
    State state;
    state.C = c;
    for (const auto row : c) {
        const int weight = std::popcount(row);
        if (weight < 1 || weight > 3) throw std::runtime_error("C row outside 1..3");
        state.score.c_weight += weight;
    }
    state.P = inverse(c);
    state.T = multiply(state.P, a_plus_i);
    state.B = multiply(multiply(state.P, a), c);
    for (int row = 0; row < N; ++row) {
        const int b_weight = std::popcount(state.B[row]);
        const int t_weight = std::popcount(state.T[row]);
        const int metric = 4 * b_weight + t_weight;
        state.score.over += metric > 16;
        state.score.excess += std::max(0, metric - 16);
        state.score.maximum = std::max(state.score.maximum, metric);
        state.score.b_weight += b_weight;
        state.score.t_weight += t_weight;
        state.score.combined_weight += b_weight + t_weight;
    }
    return state;
}

bool parse_matrix(const std::string& line, const char* name, Matrix& output) {
    const std::string marker = std::string{"\""} + name + "\":[";
    auto cursor = line.find(marker);
    if (cursor == std::string::npos) return false;
    cursor += marker.size();
    for (int row = 0; row < N; ++row) {
        cursor = line.find('"', cursor);
        if (cursor == std::string::npos || cursor + 9 >= line.size()) return false;
        output[row] = static_cast<std::uint32_t>(
            std::stoul(line.substr(cursor + 1, 8), nullptr, 16));
        cursor += 10;
    }
    return true;
}

std::vector<Matrix> load_centers(const std::string& path) {
    std::ifstream input(path);
    if (!input) throw std::runtime_error("cannot open center JSONL");
    std::vector<Matrix> result;
    std::string line;
    while (std::getline(input, line)) {
        Matrix c{};
        if (parse_matrix(line, "C", c)) result.push_back(c);
    }
    if (result.empty()) throw std::runtime_error("center JSONL contains no C matrix");
    return result;
}

void emit(std::ostream& output, std::uint64_t run, std::uint64_t step,
          const State& state) {
    output << "{\"run\":" << run << ",\"step\":" << step
           << ",\"score\":{\"over\":" << state.score.over
           << ",\"excess\":" << state.score.excess
           << ",\"max\":" << state.score.maximum
           << ",\"combined_weight\":" << state.score.combined_weight
           << ",\"B_weight\":" << state.score.b_weight
           << ",\"T_weight\":" << state.score.t_weight
           << ",\"C_weight\":" << state.score.c_weight << "},";
    const auto matrix = [&](const char* name, const Matrix& value) {
        output << "\"" << name << "\":[";
        for (int row = 0; row < N; ++row) {
            output << (row ? ",\"" : "\"") << std::hex << std::setw(8)
                   << std::setfill('0') << value[row] << "\"";
        }
        output << std::dec << ']';
    };
    matrix("T", state.T); output << ',';
    matrix("B", state.B); output << ',';
    matrix("C", state.C); output << ',';
    matrix("D", state.T);
    output << ",\"delay\":8,\"cycles\":66}\n" << std::flush;
}

std::uint32_t random_sparse_row(std::mt19937_64& rng) {
    const int weight = 1 + static_cast<int>(rng() % 3);
    std::uint32_t result = 0;
    while (std::popcount(result) < weight) result |= std::uint32_t{1} << (rng() % N);
    return result;
}

bool mutate_matrix(Matrix& c, std::mt19937_64& rng) {
    const int operation = rng() % 100;
    if (operation < 35) {
        // Right transvection C <- C*E(destination,source).
        int destination = rng() % N;
        int source = rng() % (N - 1);
        if (source >= destination) ++source;
        const auto destination_bit = std::uint32_t{1} << destination;
        const auto source_bit = std::uint32_t{1} << source;
        for (auto& row : c) {
            if (row & destination_bit) row ^= source_bit;
            const int weight = std::popcount(row);
            if (weight < 1 || weight > 3) return false;
        }
        return true;
    }
    if (operation < 60) {
        // Left transvection C <- E(destination,source)*C.
        int destination = rng() % N;
        int source = rng() % (N - 1);
        if (source >= destination) ++source;
        c[destination] ^= c[source];
        const int weight = std::popcount(c[destination]);
        return weight >= 1 && weight <= 3;
    }
    if (operation < 70) {
        int left = rng() % N;
        int right = rng() % (N - 1);
        if (right >= left) ++right;
        std::swap(c[left], c[right]);
        return true;
    }
    if (operation < 88) {
        const int row = rng() % N;
        c[row] ^= std::uint32_t{1} << (rng() % N);
        const int weight = std::popcount(c[row]);
        return weight >= 1 && weight <= 3;
    }
    c[rng() % N] = random_sparse_row(rng);
    return true;
}

bool propose(const State& current, State& proposal, const Matrix& a,
             const Matrix& a_plus_i, std::mt19937_64& rng) {
    auto c = current.C;
    const int count_roll = rng() % 1000;
    int moves = count_roll < 820 ? 1 : count_roll < 970 ? 2 : 3;
    while (moves--) {
        if (!mutate_matrix(c, rng)) return false;
    }
    try {
        proposal = make_state(c, a, a_plus_i);
        return true;
    } catch (const std::runtime_error&) {
        return false;
    }
}

}  // namespace

int main(int argc, char** argv) {
    if (argc < 6) {
        std::cerr << "usage: search_sparse_c66 STEPS RESTARTS SEED CENTERS OUTPUT\n";
        return 4;
    }
    const auto steps = std::stoull(argv[1]);
    const int restarts = std::stoi(argv[2]);
    const auto seed = std::stoull(argv[3], nullptr, 0);
    const std::string center_path = argv[4];
    const std::string output_path = argv[5];
    const auto a = transition();
    auto a_plus_i = a;
    for (int bit = 0; bit < N; ++bit) a_plus_i[bit] ^= std::uint32_t{1} << bit;
    const auto centers = load_centers(center_path);
    State global;
    global.score.over = std::numeric_limits<int>::max();
    global.score.excess = std::numeric_limits<int>::max();
    for (const auto& c : centers) {
        try {
            auto state = make_state(c, a, a_plus_i);
            if (state.score.key() < global.score.key()) global = std::move(state);
        } catch (const std::runtime_error&) {
        }
    }
    if (global.score.over == std::numeric_limits<int>::max()) return 5;
    std::ofstream output(output_path, std::ios::app);
    if (!output) return 3;
    emit(output, 0, 0, global);

    if (argc >= 7) {
        State second;
        second.score.over = std::numeric_limits<int>::max();
        second.score.excess = std::numeric_limits<int>::max();
        for (const auto& c : load_centers(argv[6])) {
            try {
                auto state = make_state(c, a, a_plus_i);
                if (state.score.key() < second.score.key()) second = std::move(state);
            } catch (const std::runtime_error&) {
            }
        }
        if (second.score.over == std::numeric_limits<int>::max()) return 6;
        std::vector<int> different_rows;
        for (int row = 0; row < N; ++row) {
            if (global.C[row] != second.C[row]) different_rows.push_back(row);
        }
        if (different_rows.size() > 25) {
            std::cerr << "crossover has too many differing rows: "
                      << different_rows.size() << "\n";
            return 7;
        }
        const auto combinations = std::uint64_t{1} << different_rows.size();
        std::uint64_t nonsingular = 0;
        for (std::uint64_t mask = 1; mask < combinations; ++mask) {
            auto c = global.C;
            for (int index = 0; index < static_cast<int>(different_rows.size()); ++index) {
                if ((mask >> index) & 1U) c[different_rows[index]] = second.C[different_rows[index]];
            }
            try {
                auto candidate = make_state(c, a, a_plus_i);
                ++nonsingular;
                if (candidate.score.key() < global.score.key()) {
                    global = std::move(candidate);
                    emit(output, 1, mask, global);
                    std::cerr << "crossover mask=" << mask
                              << " over=" << global.score.over
                              << " excess=" << global.score.excess
                              << " max=" << global.score.maximum << "\n";
                    if (global.score.over == 0) return 0;
                }
            } catch (const std::runtime_error&) {
            }
        }
        std::cerr << "crossover complete rows=" << different_rows.size()
                  << " combinations=" << combinations
                  << " nonsingular=" << nonsingular << "\n";
        return 2;
    }

    std::mt19937_64 rng(seed);
    std::uniform_real_distribution<double> unit(0.0, 1.0);
    constexpr std::uint64_t window = 250'000;
    for (int restart = 0; restart < restarts; ++restart) {
        auto current = global;
        for (int move = 0, count = restart == 0 ? 0 : 2 + rng() % 12;
             move < count; ++move) {
            State perturbed;
            if (propose(current, perturbed, a, a_plus_i, rng)) current = std::move(perturbed);
        }
        for (std::uint64_t step = 1; step <= steps; ++step) {
            const auto in_window = (step - 1) % window;
            if (in_window == 0 && step != 1) current = global;
            State candidate;
            if (!propose(current, candidate, a, a_plus_i, rng)) continue;
            const double phase = static_cast<double>(in_window) / window;
            const double temperature = 1.5e5 * std::pow(1.0 - phase, 3) + 25.0;
            const double delta = candidate.score.energy() - current.score.energy();
            if (delta <= 0 || unit(rng) < std::exp(-delta / temperature)) {
                current = std::move(candidate);
            }
            if (current.score.key() < global.score.key()) {
                global = current;
                emit(output, restart, step, global);
                std::cerr << "best run=" << restart << " step=" << step
                          << " over=" << global.score.over
                          << " excess=" << global.score.excess
                          << " max=" << global.score.maximum
                          << " weight=" << global.score.combined_weight << "\n";
                if (global.score.over == 0) return 0;
            }
        }
    }
    return 2;
}
