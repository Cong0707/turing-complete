#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <queue>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <unordered_set>
#include <vector>

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
    for (int bit = 0; bit < N; ++bit) result[bit] = std::uint32_t{1} << bit;
    return result;
}

Matrix transition() {
    Matrix result{};
    for (int source = 0; source < N; ++source) {
        const auto value = xorshift32(std::uint32_t{1} << source);
        for (int target = 0; target < N; ++target) {
            result[target] |= ((value >> target) & 1U) << source;
        }
    }
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
    auto result = identity();
    for (int column = 0; column < N; ++column) {
        int pivot = column;
        while (pivot < N && ((matrix[pivot] >> column) & 1U) == 0) ++pivot;
        if (pivot == N) throw std::runtime_error("singular matrix");
        std::swap(matrix[pivot], matrix[column]);
        std::swap(result[pivot], result[column]);
        for (int row = 0; row < N; ++row) {
            if (row != column && ((matrix[row] >> column) & 1U)) {
                matrix[row] ^= matrix[column];
                result[row] ^= result[column];
            }
        }
    }
    return result;
}

struct State {
    Matrix T{};
    Matrix B{};
    Matrix C{};
    Matrix D{};
};

Matrix A;
Matrix A_plus_I;

State derive(const Matrix& t) {
    const auto t_inverse = inverse(t);
    return {t, multiply(multiply(t, A), t_inverse),
            multiply(A_plus_I, t_inverse), t};
}

struct Score {
    int over = 0;
    int excess = 0;
    int maximum = 0;
    int feedback_weight = 0;
    int c_weight = 0;
    int squared_slack = 0;
    int switch_units = 0;

    auto key() const {
        return std::tuple(over, excess, maximum, feedback_weight, c_weight,
                          squared_slack);
    }
};

Score evaluate(const State& state) {
    Score result;
    for (int row = 0; row < N; ++row) {
        if (std::popcount(state.C[row]) > 3) {
            result.over += N;
            result.excess += 100 + std::popcount(state.C[row]) - 3;
        }
        const int load = 4 * std::popcount(state.B[row])
                       + std::popcount(state.D[row]);
        result.over += load > 16;
        const int overload = std::max(0, load - 16);
        result.excess += overload;
        result.switch_units += (overload + 7) / 8;
        result.maximum = std::max(result.maximum, load);
        result.feedback_weight += std::popcount(state.B[row])
                                + std::popcount(state.D[row]);
        result.c_weight += std::popcount(state.C[row]);
        const int slack = 16 - load;
        result.squared_slack += slack * slack;
    }
    return result;
}

bool parse_matrix(const std::string& line, const std::string& name, Matrix& out) {
    const auto marker = std::string{"\""} + name + "\":[";
    auto cursor = line.find(marker);
    if (cursor == std::string::npos) return false;
    cursor += marker.size();
    for (int row = 0; row < N; ++row) {
        cursor = line.find('"', cursor);
        if (cursor == std::string::npos || cursor + 9 >= line.size()) return false;
        out[row] = static_cast<std::uint32_t>(
            std::stoul(line.substr(cursor + 1, 8), nullptr, 16));
        cursor += 10;
    }
    return true;
}

State load_best(const std::string& path) {
    std::ifstream input(path);
    if (!input) throw std::runtime_error("cannot open seed JSONL");
    State best{};
    Score best_score;
    best_score.over = std::numeric_limits<int>::max();
    std::string line;
    while (std::getline(input, line)) {
        Matrix t{};
        if (!parse_matrix(line, "T", t)) continue;
        const auto state = derive(t);
        const auto score = evaluate(state);
        if (score.key() < best_score.key()) {
            best = state;
            best_score = score;
        }
    }
    if (best_score.over == std::numeric_limits<int>::max()) {
        throw std::runtime_error("seed JSONL has no T matrix");
    }
    return best;
}

std::vector<std::uint32_t> legal_vectors(const State& state, int destination) {
    const auto destination_bit = std::uint32_t{1} << destination;
    int pivot = -1;
    for (int row = 0; row < N; ++row) {
        if (state.C[row] & destination_bit) {
            pivot = row;
            break;
        }
    }
    if (pivot < 0) throw std::runtime_error("invertible C has an empty column");

    std::vector<std::uint32_t> result;
    result.reserve(496);
    const auto consider_target = [&](std::uint32_t target) {
        const auto vector = state.C[pivot] ^ target;
        if (!vector || (vector & destination_bit)) return;
        for (int row = 0; row < N; ++row) {
            if ((state.C[row] & destination_bit)
                && std::popcount(state.C[row] ^ vector) > 3) return;
        }
        result.push_back(vector);
    };

    consider_target(destination_bit);
    for (int first = 0; first < N; ++first) {
        if (first == destination) continue;
        const auto one = destination_bit | (std::uint32_t{1} << first);
        consider_target(one);
        for (int second = first + 1; second < N; ++second) {
            if (second == destination) continue;
            consider_target(one | (std::uint32_t{1} << second));
        }
    }
    std::sort(result.begin(), result.end());
    result.erase(std::unique(result.begin(), result.end()), result.end());
    return result;
}

void transvection(State& state, int destination, std::uint32_t vector) {
    const auto destination_bit = std::uint32_t{1} << destination;
    state.T[destination] ^= apply_row(vector, state.T);
    state.D[destination] ^= apply_row(vector, state.D);
    for (auto& row : state.B) {
        if (row & destination_bit) row ^= vector;
    }
    state.B[destination] ^= apply_row(vector, state.B);
    for (auto& row : state.C) {
        if (row & destination_bit) row ^= vector;
    }
}

void verify(const State& state) {
    const auto rebuilt = derive(state.T);
    if (rebuilt.B != state.B || rebuilt.C != state.C || rebuilt.D != state.D) {
        throw std::runtime_error("incremental transvection identity failed");
    }
    for (const auto row : state.C) {
        if (std::popcount(row) > 3) {
            throw std::runtime_error("output capacity failed");
        }
    }
}

std::uint64_t fingerprint(const Matrix& matrix) {
    std::uint64_t result = 0xcbf29ce484222325ULL;
    for (const auto row : matrix) {
        result ^= row;
        result *= 0x100000001b3ULL;
        result ^= result >> 29;
    }
    return result;
}

void emit(std::ostream& output, int layer, std::uint64_t checked,
          const State& state, const Score& score) {
    output << "{\"layer\":" << layer << ",\"checked\":" << checked
           << ",\"score\":{\"over\":" << score.over
           << ",\"excess\":" << score.excess
           << ",\"max\":" << score.maximum
           << ",\"feedback_weight\":" << score.feedback_weight
           << ",\"c_weight\":" << score.c_weight
           << ",\"squared_slack\":" << score.squared_slack
           << ",\"switch_units\":" << score.switch_units << "},";
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
    matrix("D", state.D); output << "}\n" << std::flush;
}

struct Node {
    State state{};
    Score score{};
    int last_destination = -1;
    std::uint32_t last_vector = 0;
    std::uint64_t hash = 0;
};

auto node_key(const Node& node) {
    return std::tuple_cat(node.score.key(), std::tuple(node.hash));
}

struct WorseFirst {
    bool operator()(const Node& left, const Node& right) const {
        return node_key(left) < node_key(right);
    }
};

}  // namespace

#ifndef RNG65_LEGAL_TRANSVECTION_LIBRARY
int main(int argc, char** argv) {
    if (argc < 3) {
        std::cerr << "usage: search_legal_transvections seed.jsonl output.jsonl "
                     "[depth] [width] [oversample] [strata]\n";
        return 4;
    }
    const int depth = argc > 3 ? std::stoi(argv[3]) : 24;
    const int width = argc > 4 ? std::stoi(argv[4]) : 512;
    const int oversample_factor = argc > 5 ? std::stoi(argv[5]) : 8;
    const int strata = argc > 6 ? std::stoi(argv[6]) : 1;
    if (strata < 1 || strata > 16) return 5;
    A = transition();
    A_plus_I = A;
    for (int bit = 0; bit < N; ++bit) A_plus_I[bit] ^= std::uint32_t{1} << bit;

    auto global_state = load_best(argv[1]);
    auto global = evaluate(global_state);
    verify(global_state);
    std::ofstream output(argv[2], std::ios::app);
    if (!output) return 3;
    emit(output, 0, 0, global_state, global);
    std::vector<Node> beam{{global_state, global, -1, 0,
                            fingerprint(global_state.T)}};
    std::uint64_t checked = 0;
    const auto bucket_width = static_cast<std::size_t>(
        std::max(1, (width + strata - 1) / strata));
    const auto capacity = bucket_width
                        * static_cast<std::size_t>(oversample_factor);

    for (int layer = 1; layer <= depth; ++layer) {
        std::array<std::priority_queue<Node, std::vector<Node>, WorseFirst>, 64>
            queues;
        auto retain = [&](Node candidate) {
            if (candidate.score.over < 0 || candidate.score.over >= 64) return;
            auto& queue = queues[candidate.score.over];
            if (queue.size() < capacity) {
                queue.push(std::move(candidate));
            } else if (node_key(candidate) < node_key(queue.top())) {
                queue.pop();
                queue.push(std::move(candidate));
            }
        };
        for (const auto& parent : beam) {
            retain(parent);
            for (int destination = 0; destination < N; ++destination) {
                for (const auto vector : legal_vectors(parent.state, destination)) {
                    if (destination == parent.last_destination
                        && vector == parent.last_vector) continue;
                    Node candidate;
                    candidate.state = parent.state;
                    transvection(candidate.state, destination, vector);
                    candidate.score = evaluate(candidate.state);
                    candidate.last_destination = destination;
                    candidate.last_vector = vector;
                    candidate.hash = fingerprint(candidate.state.T);
                    ++checked;
                    if (candidate.score.key() < global.key()) {
                        verify(candidate.state);
                        global = candidate.score;
                        global_state = candidate.state;
                        emit(output, layer, checked, global_state, global);
                        std::cerr << "best layer=" << layer
                                  << " checked=" << checked
                                  << " over=" << global.over
                                  << " excess=" << global.excess
                                  << " max=" << global.maximum
                                  << " fw=" << global.feedback_weight
                                  << " cw=" << global.c_weight << "\n";
                        if (global.over == 0) return 0;
                    }
                    retain(std::move(candidate));
                }
            }
        }

        std::vector<Node> ordered;
        const int first_bucket = global.over;
        const int last_bucket = std::min(63, first_bucket + strata - 1);
        for (int bucket = first_bucket; bucket <= last_bucket; ++bucket) {
            auto& queue = queues[bucket];
            while (!queue.empty()) {
                ordered.push_back(queue.top());
                queue.pop();
            }
        }
        std::sort(ordered.begin(), ordered.end(),
                  [](const Node& left, const Node& right) {
                      return node_key(left) < node_key(right);
                  });
        beam.clear();
        std::unordered_set<std::uint64_t> seen;
        std::array<int, 64> selected{};
        for (auto& candidate : ordered) {
            if (!seen.insert(candidate.hash).second) continue;
            if (selected[candidate.score.over]
                >= static_cast<int>(bucket_width)) continue;
            ++selected[candidate.score.over];
            beam.push_back(std::move(candidate));
            if (static_cast<int>(beam.size()) >= width) break;
        }
        if (beam.empty()) break;
        std::cerr << "layer=" << layer << " checked=" << checked
                  << " beam=" << beam.size() << " front="
                  << beam.front().score.over << '/'
                  << beam.front().score.excess << '/'
                  << beam.front().score.maximum << " global="
                  << global.over << '/' << global.excess << '/'
                  << global.maximum << "\n";
    }
    return global.over == 0 ? 0 : 2;
}
#endif
