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
#include <unordered_set>
#include <vector>

namespace {

constexpr int N = 32;
using Matrix = std::array<std::uint32_t, N>;

struct State {
    Matrix C{};
    Matrix T{};
    Matrix B{};
    Matrix D{};
};

struct Score {
    int over = 0;
    int excess = 0;
    int square_excess = 0;
    int maximum = 0;
    int feedback_weight = 0;
    int output_weight = 0;

    auto key() const {
        return std::tuple(over, excess, maximum, square_excess,
                          feedback_weight, output_weight);
    }

    double energy() const {
        // The squared term gives a gradient for the metric-30 obstruction,
        // while the first term still strongly prefers removing a bad row.
        return 2.0e6 * over + 4.0e4 * excess
             + 2.0e3 * square_excess + 200.0 * maximum
             + feedback_weight;
    }
};

std::uint32_t xorshift32(std::uint32_t value) {
    value ^= value >> 13;
    value ^= value << 17;
    value ^= value >> 5;
    return value;
}

Matrix identity() {
    Matrix result{};
    for (int row = 0; row < N; ++row) result[row] = std::uint32_t{1} << row;
    return result;
}

Matrix transition() {
    Matrix result{};
    for (int source = 0; source < N; ++source) {
        const auto column = xorshift32(std::uint32_t{1} << source);
        for (int row = 0; row < N; ++row) {
            result[row] |= ((column >> row) & 1U) << source;
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

bool inverse(Matrix matrix, Matrix& result) {
    result = identity();
    for (int column = 0; column < N; ++column) {
        int pivot = column;
        while (pivot < N && ((matrix[pivot] >> column) & 1U) == 0) ++pivot;
        if (pivot == N) return false;
        std::swap(matrix[column], matrix[pivot]);
        std::swap(result[column], result[pivot]);
        for (int row = 0; row < N; ++row) {
            if (row != column && ((matrix[row] >> column) & 1U)) {
                matrix[row] ^= matrix[column];
                result[row] ^= result[column];
            }
        }
    }
    return true;
}

State derive(const Matrix& C, const Matrix& A, const Matrix& A_plus_I) {
    State state;
    state.C = C;
    if (!inverse(C, state.T)) throw std::runtime_error("singular C");
    state.B = multiply(multiply(state.T, A), C);
    state.D = multiply(state.T, A_plus_I);
    return state;
}

Score evaluate(const State& state) {
    Score result;
    for (int row = 0; row < N; ++row) {
        const int c_weight = std::popcount(state.C[row]);
        if (c_weight > 3) {
            result.over += 1000;
            result.excess += c_weight - 3;
        }
        result.output_weight += c_weight;
        const int b_weight = std::popcount(state.B[row]);
        const int d_weight = std::popcount(state.D[row]);
        const int metric = 4 * b_weight + d_weight;
        const int excess = std::max(0, metric - 16);
        result.over += metric > 16;
        result.excess += excess;
        result.square_excess += excess * excess;
        result.maximum = std::max(result.maximum, metric);
        result.feedback_weight += b_weight + d_weight;
    }
    return result;
}

Matrix structured_seed_C() {
    return {
        0x08020020U, 0x10040040U, 0x20080080U, 0x42100000U,
        0x84200000U, 0x00400021U, 0x00800042U, 0x01000084U,
        0x02000108U, 0x04000210U, 0x00000401U, 0x00000802U,
        0x0000100cU, 0x00042008U, 0x00084010U, 0x00008000U,
        0x00010002U, 0x00020000U, 0x00040000U, 0x00080000U,
        0x02100000U, 0x04200000U, 0x00400001U, 0x00800002U,
        0x01000004U, 0x02000008U, 0x04000010U, 0x00000001U,
        0x00000002U, 0x00000004U, 0x00000008U, 0x00000010U,
    };
}

Matrix rank1_seed_C() {
    auto result = structured_seed_C();
    result[0] = 0x0c020000U;
    result[13] = 0x00002008U;
    return result;
}

Matrix over3_seed_C() {
    return {
        0x00001480U, 0x00804040U, 0x21080000U, 0x40100800U,
        0x84200000U, 0x00400401U, 0x10800002U, 0x01008004U,
        0x00100108U, 0x04000210U, 0x00000021U, 0x00020002U,
        0x08000004U, 0x00002008U, 0x00040010U, 0x02000000U,
        0x00010002U, 0x00000480U, 0x00800040U, 0x21000000U,
        0x00100800U, 0x84000000U, 0x00000401U, 0x00800002U,
        0x01000004U, 0x00100008U, 0x04000010U, 0x00000001U,
        0x00000002U, 0x00000004U, 0x00000008U, 0x00000010U,
    };
}

Matrix joint_over3_seed_C() {
    return {
        0x08420000U, 0x10802000U, 0x21004000U, 0x42100000U,
        0x84200000U, 0x00400021U, 0x00800042U, 0x01000084U,
        0x02000108U, 0x04000210U, 0x00000401U, 0x00000802U,
        0x00001004U, 0x00040008U, 0x00080010U, 0x00008000U,
        0x00010002U, 0x00420000U, 0x00802000U, 0x01004000U,
        0x02100000U, 0x04200000U, 0x00400001U, 0x00800002U,
        0x01000004U, 0x02000008U, 0x04000010U, 0x00000001U,
        0x00000002U, 0x00000004U, 0x00000008U, 0x00000010U,
    };
}

void right_transvection(State& state, int destination, int source) {
    const auto destination_bit = std::uint32_t{1} << destination;
    const auto source_bit = std::uint32_t{1} << source;
    state.T[destination] ^= state.T[source];
    for (auto& row : state.B) {
        if (row & destination_bit) row ^= source_bit;
    }
    state.B[destination] ^= state.B[source];
    for (auto& row : state.C) {
        if (row & destination_bit) row ^= source_bit;
    }
    state.D[destination] ^= state.D[source];
}

bool output_valid(const Matrix& C) {
    return std::all_of(C.begin(), C.end(), [](std::uint32_t row) {
        return std::popcount(row) <= 3;
    });
}

bool replay_identity(const State& state, const Matrix& A,
                     const Matrix& A_plus_I) {
    Matrix inverse_check{};
    if (!inverse(state.C, inverse_check) || inverse_check != state.T) return false;
    if (multiply(multiply(state.T, A), state.C) != state.B) return false;
    if (multiply(state.T, A_plus_I) != state.D) return false;
    return multiply(state.C, state.T) == identity()
        && multiply(state.T, state.C) == identity();
}

void emit(std::ostream& output, const std::string& mode, std::uint64_t step,
          const State& state, const Score& score) {
    output << "{\"mode\":\"" << mode << "\",\"step\":" << step
           << ",\"score\":{\"over\":" << score.over
           << ",\"excess\":" << score.excess
           << ",\"square_excess\":" << score.square_excess
           << ",\"maximum\":" << score.maximum
           << ",\"feedback_weight\":" << score.feedback_weight
           << ",\"output_weight\":" << score.output_weight << "},";
    const auto matrix = [&](const char* name, const Matrix& value) {
        output << "\"" << name << "\":[";
        for (int row = 0; row < N; ++row) {
            output << (row ? ",\"" : "\"") << std::hex << std::setw(8)
                   << std::setfill('0') << value[row] << "\"";
        }
        output << std::dec << ']';
    };
    matrix("C", state.C); output << ',';
    matrix("T0", state.T); output << ',';
    matrix("B", state.B); output << ',';
    matrix("D", state.D);
    output << "}\n" << std::flush;
}

std::vector<std::uint32_t> sparse_rows() {
    std::vector<std::uint32_t> result;
    result.reserve(5488);
    for (int first = 0; first < N; ++first) {
        result.push_back(std::uint32_t{1} << first);
        for (int second = first + 1; second < N; ++second) {
            result.push_back((std::uint32_t{1} << first)
                           | (std::uint32_t{1} << second));
            for (int third = second + 1; third < N; ++third) {
                result.push_back((std::uint32_t{1} << first)
                               | (std::uint32_t{1} << second)
                               | (std::uint32_t{1} << third));
            }
        }
    }
    return result;
}

bool replace_row(const State& current, int destination, std::uint32_t value,
                 const Matrix& A, const Matrix& A_plus_I, State& result) {
    if (value == current.C[destination]) return false;
    const auto delta = value ^ current.C[destination];
    const auto inverse_delta = apply_row(delta, current.T);
    if ((inverse_delta >> destination) & 1U) return false;

    result = current;
    result.C[destination] = value;
    const auto destination_bit = std::uint32_t{1} << destination;
    for (int row = 0; row < N; ++row) {
        if (result.T[row] & destination_bit) result.T[row] ^= inverse_delta;
    }
    result.B = multiply(multiply(result.T, A), result.C);
    result.D = multiply(result.T, A_plus_I);
    return true;
}

void exact_transvection_radius2(const State& seed, const Matrix& A,
                                const Matrix& A_plus_I,
                                std::ostream& output) {
    auto best = seed;
    auto best_score = evaluate(seed);
    std::uint64_t checked = 0;
    std::uint64_t valid = 0;
    for (int d1 = 0; d1 < N; ++d1) {
        for (int s1 = 0; s1 < N; ++s1) {
            if (d1 == s1) continue;
            auto first = seed;
            right_transvection(first, d1, s1);
            if (output_valid(first.C)) {
                ++valid;
                const auto score = evaluate(first);
                if (score.key() < best_score.key()) {
                    best = first;
                    best_score = score;
                    emit(output, "radius2", ++checked, best, best_score);
                }
            }
            for (int d2 = 0; d2 < N; ++d2) {
                for (int s2 = 0; s2 < N; ++s2) {
                    if (d2 == s2 || (d1 == d2 && s1 == s2)) continue;
                    ++checked;
                    auto candidate = first;
                    right_transvection(candidate, d2, s2);
                    if (!output_valid(candidate.C)) continue;
                    ++valid;
                    const auto score = evaluate(candidate);
                    if (score.key() < best_score.key()) {
                        best = candidate;
                        best_score = score;
                        emit(output, "radius2", checked, best, best_score);
                        std::cerr << "radius2 best checked=" << checked
                                  << " over=" << best_score.over
                                  << " excess=" << best_score.excess
                                  << " max=" << best_score.maximum << '\n';
                    }
                }
            }
        }
    }
    if (!replay_identity(best, A, A_plus_I)) {
        throw std::runtime_error("radius2 incremental identity failed");
    }
    std::cerr << "radius2 complete checked=" << checked
              << " valid=" << valid << " best=" << best_score.over << '/'
              << best_score.excess << '/' << best_score.maximum << '\n';
    output << "{\"mode\":\"radius2-summary\",\"checked\":" << checked
           << ",\"valid_final_C\":" << valid << ",\"best\":["
           << best_score.over << ',' << best_score.excess << ','
           << best_score.maximum << "]}\n" << std::flush;
}

State exact_rank1_pass(const State& start, const Matrix& A,
                       const Matrix& A_plus_I,
                       const std::vector<std::uint32_t>& rows,
                       std::ostream& output, std::uint64_t& checked,
                       bool& improved) {
    auto best = start;
    auto best_score = evaluate(start);
    for (int destination = 0; destination < N; ++destination) {
        for (const auto value : rows) {
            ++checked;
            State candidate;
            if (!replace_row(start, destination, value, A, A_plus_I, candidate)) {
                continue;
            }
            const auto score = evaluate(candidate);
            if (score.key() < best_score.key()) {
                best = candidate;
                best_score = score;
                emit(output, "rank1", checked, best, best_score);
                std::cerr << "rank1 best checked=" << checked
                          << " over=" << best_score.over
                          << " excess=" << best_score.excess
                          << " max=" << best_score.maximum << '\n';
            }
        }
    }
    improved = best_score.key() < evaluate(start).key();
    if (!replay_identity(best, A, A_plus_I)) {
        throw std::runtime_error("rank1 update identity failed");
    }
    return best;
}

void coordinate_descent(const State& seed, int passes, const Matrix& A,
                        const Matrix& A_plus_I, std::ostream& output) {
    const auto rows = sparse_rows();
    auto current = seed;
    std::uint64_t checked = 0;
    for (int pass = 0; pass < passes; ++pass) {
        bool improved = false;
        current = exact_rank1_pass(current, A, A_plus_I, rows, output,
                                   checked, improved);
        const auto score = evaluate(current);
        std::cerr << "rank1 pass=" << pass << " checked=" << checked
                  << " best=" << score.over << '/' << score.excess << '/'
                  << score.maximum << '\n';
        if (!improved || score.over == 0) break;
    }
    const auto final_score = evaluate(current);
    output << "{\"mode\":\"rank1-summary\",\"checked\":" << checked
           << ",\"best\":[" << final_score.over << ',' << final_score.excess
           << ',' << final_score.maximum << "]}\n" << std::flush;
}

int feedback_metric(const State& state, int row) {
    return 4 * std::popcount(state.B[row]) + std::popcount(state.D[row]);
}

struct RowMove {
    int destination = 0;
    std::uint32_t value = 0;
    Score score{};
    std::array<int, 3> bad_metrics{};
};

void rank2_pool_search(const State& seed, int pool_per_objective,
                       const Matrix& A, const Matrix& A_plus_I,
                       std::ostream& output) {
    const auto rows = sparse_rows();
    std::vector<int> bad_rows;
    for (int row = 0; row < N; ++row) {
        if (feedback_metric(seed, row) > 16) bad_rows.push_back(row);
    }
    if (bad_rows.size() != 3) {
        throw std::runtime_error("rank2 pool expects exactly three bad rows");
    }

    std::vector<RowMove> moves;
    moves.reserve(100'000);
    std::uint64_t rank1_checked = 0;
    for (int destination = 0; destination < N; ++destination) {
        for (const auto value : rows) {
            ++rank1_checked;
            State candidate;
            if (!replace_row(seed, destination, value, A, A_plus_I, candidate)) {
                continue;
            }
            RowMove move;
            move.destination = destination;
            move.value = value;
            move.score = evaluate(candidate);
            for (int index = 0; index < 3; ++index) {
                move.bad_metrics[index] = feedback_metric(candidate, bad_rows[index]);
            }
            moves.push_back(move);
        }
    }

    std::unordered_set<std::uint64_t> selected_keys;
    std::vector<RowMove> pool;
    const auto add_best = [&](auto comparator) {
        std::vector<std::size_t> order(moves.size());
        for (std::size_t index = 0; index < order.size(); ++index) order[index] = index;
        const auto keep = std::min<std::size_t>(pool_per_objective, order.size());
        std::partial_sort(order.begin(), order.begin() + keep, order.end(),
                          [&](std::size_t left, std::size_t right) {
                              return comparator(moves[left], moves[right]);
                          });
        for (std::size_t index = 0; index < keep; ++index) {
            const auto& move = moves[order[index]];
            const auto key = (static_cast<std::uint64_t>(move.destination) << 32)
                           | move.value;
            if (selected_keys.insert(key).second) pool.push_back(move);
        }
    };

    add_best([](const RowMove& left, const RowMove& right) {
        return left.score.key() < right.score.key();
    });
    add_best([](const RowMove& left, const RowMove& right) {
        return left.score.energy() < right.score.energy();
    });
    for (int bad_index = 0; bad_index < 3; ++bad_index) {
        add_best([bad_index](const RowMove& left, const RowMove& right) {
            return std::tuple(left.bad_metrics[bad_index], left.score.energy())
                 < std::tuple(right.bad_metrics[bad_index], right.score.energy());
        });
    }
    add_best([](const RowMove& left, const RowMove& right) {
        const int left_sum = left.bad_metrics[0] + left.bad_metrics[1]
                           + left.bad_metrics[2];
        const int right_sum = right.bad_metrics[0] + right.bad_metrics[1]
                            + right.bad_metrics[2];
        return std::tuple(left_sum, left.score.energy())
             < std::tuple(right_sum, right.score.energy());
    });

    auto best = seed;
    auto best_score = evaluate(seed);
    std::uint64_t checked = 0;
    std::uint64_t nonsingular = 0;
    for (std::size_t first = 0; first < pool.size(); ++first) {
        for (std::size_t second = first + 1; second < pool.size(); ++second) {
            if (pool[first].destination == pool[second].destination) continue;
            ++checked;
            auto C = seed.C;
            C[pool[first].destination] = pool[first].value;
            C[pool[second].destination] = pool[second].value;
            Matrix T{};
            if (!inverse(C, T)) continue;
            ++nonsingular;
            State candidate;
            candidate.C = C;
            candidate.T = T;
            candidate.B = multiply(multiply(T, A), C);
            candidate.D = multiply(T, A_plus_I);
            const auto score = evaluate(candidate);
            if (score.key() < best_score.key()) {
                best = candidate;
                best_score = score;
                emit(output, "rank2pool", checked, best, best_score);
                std::cerr << "rank2pool best checked=" << checked
                          << " score=" << best_score.over << '/'
                          << best_score.excess << '/' << best_score.maximum << '\n';
            }
        }
    }
    if (!replay_identity(best, A, A_plus_I)) {
        throw std::runtime_error("rank2 pool identity failed");
    }
    std::cerr << "rank2pool complete rank1=" << rank1_checked
              << " legal_rank1=" << moves.size() << " pool=" << pool.size()
              << " pairs=" << checked << " nonsingular=" << nonsingular
              << " best=" << best_score.over << '/' << best_score.excess
              << '/' << best_score.maximum << '\n';
    output << "{\"mode\":\"rank2pool-summary\",\"rank1_checked\":"
           << rank1_checked << ",\"legal_rank1\":" << moves.size()
           << ",\"pool\":" << pool.size() << ",\"pairs\":" << checked
           << ",\"nonsingular\":" << nonsingular << ",\"best\":["
           << best_score.over << ',' << best_score.excess << ','
           << best_score.maximum << "]}\n" << std::flush;
}

void crossmix_search(const Matrix& left_C, const Matrix& right_C,
                     const Matrix& A, const Matrix& A_plus_I,
                     std::ostream& output) {
    std::vector<int> differences;
    for (int row = 0; row < N; ++row) {
        if (left_C[row] != right_C[row]) differences.push_back(row);
    }
    if (differences.size() >= 63) {
        throw std::runtime_error("crossmix mask does not fit uint64");
    }
    auto best = derive(left_C, A, A_plus_I);
    auto best_score = evaluate(best);
    const auto combinations = std::uint64_t{1} << differences.size();
    std::uint64_t nonsingular = 0;
    for (std::uint64_t mask = 0; mask < combinations; ++mask) {
        auto C = left_C;
        for (std::size_t bit = 0; bit < differences.size(); ++bit) {
            if ((mask >> bit) & 1U) C[differences[bit]] = right_C[differences[bit]];
        }
        Matrix T{};
        if (!inverse(C, T)) continue;
        ++nonsingular;
        State candidate;
        candidate.C = C;
        candidate.T = T;
        candidate.B = multiply(multiply(T, A), C);
        candidate.D = multiply(T, A_plus_I);
        const auto score = evaluate(candidate);
        if (score.key() < best_score.key()) {
            best = candidate;
            best_score = score;
            emit(output, "crossmix", mask, best, best_score);
            std::cerr << "crossmix best mask=" << mask << " score="
                      << best_score.over << '/' << best_score.excess << '/'
                      << best_score.maximum << '\n';
        }
    }
    if (!replay_identity(best, A, A_plus_I)) {
        throw std::runtime_error("crossmix identity failed");
    }
    std::cerr << "crossmix complete differing_rows=" << differences.size()
              << " combinations=" << combinations
              << " nonsingular=" << nonsingular << " best="
              << best_score.over << '/' << best_score.excess << '/'
              << best_score.maximum << '\n';
    output << "{\"mode\":\"crossmix-summary\",\"differing_rows\":"
           << differences.size() << ",\"combinations\":" << combinations
           << ",\"nonsingular\":" << nonsingular << ",\"best\":["
           << best_score.over << ',' << best_score.excess << ','
           << best_score.maximum << "]}\n" << std::flush;
}

void rank2_heavy_search(const State& seed, const Matrix& A,
                        const Matrix& A_plus_I, std::ostream& output,
                        bool include_all_bad_rows) {
    int heavy_row = 0;
    for (int row = 1; row < N; ++row) {
        if (feedback_metric(seed, row) > feedback_metric(seed, heavy_row)) {
            heavy_row = row;
        }
    }
    const auto TA = multiply(seed.T, A);
    auto sensitive_mask = seed.T[heavy_row] | TA[heavy_row];
    if (include_all_bad_rows) {
        for (int row = 0; row < N; ++row) {
            if (feedback_metric(seed, row) > 16) {
                sensitive_mask |= seed.T[row] | TA[row];
            }
        }
    }
    std::vector<int> sensitive;
    for (int bit = 0; bit < N; ++bit) {
        if ((sensitive_mask >> bit) & 1U) sensitive.push_back(bit);
    }

    const auto rows = sparse_rows();
    std::array<std::vector<std::uint32_t>, N> legal_values;
    std::uint64_t rank1_checked = 0;
    for (const int destination : sensitive) {
        for (const auto value : rows) {
            ++rank1_checked;
            State ignored;
            if (replace_row(seed, destination, value, A, A_plus_I, ignored)) {
                legal_values[destination].push_back(value);
            }
        }
    }

    auto best = seed;
    auto best_score = evaluate(seed);
    std::uint64_t checked = 0;
    std::uint64_t nonsingular = 0;
    for (std::size_t first_index = 0; first_index < sensitive.size(); ++first_index) {
        const int first = sensitive[first_index];
        for (std::size_t second_index = first_index + 1;
             second_index < sensitive.size(); ++second_index) {
            const int second = sensitive[second_index];
            for (const auto first_value : legal_values[first]) {
                for (const auto second_value : legal_values[second]) {
                    ++checked;
                    auto C = seed.C;
                    C[first] = first_value;
                    C[second] = second_value;
                    Matrix T{};
                    if (!inverse(C, T)) continue;
                    ++nonsingular;
                    State candidate;
                    candidate.C = C;
                    candidate.T = T;
                    candidate.B = multiply(multiply(T, A), C);
                    candidate.D = multiply(T, A_plus_I);
                    const auto score = evaluate(candidate);
                    if (score.key() < best_score.key()) {
                        best = candidate;
                        best_score = score;
                        emit(output, include_all_bad_rows ? "rank2bad" : "rank2heavy",
                             checked, best, best_score);
                        std::cerr << (include_all_bad_rows ? "rank2bad" : "rank2heavy")
                                  << " best pair=" << first << ',' << second
                                  << " checked=" << checked << " score="
                                  << best_score.over << '/' << best_score.excess
                                  << '/' << best_score.maximum << '\n';
                    }
                }
            }
        }
    }
    if (!replay_identity(best, A, A_plus_I)) {
        throw std::runtime_error("rank2 heavy identity failed");
    }
    std::cerr << (include_all_bad_rows ? "rank2bad" : "rank2heavy")
              << " complete heavy_row=" << heavy_row
              << " sensitive=" << sensitive.size() << " rank1=" << rank1_checked
              << " pairs=" << checked << " nonsingular=" << nonsingular
              << " best=" << best_score.over << '/' << best_score.excess
              << '/' << best_score.maximum << '\n';
    output << "{\"mode\":\""
           << (include_all_bad_rows ? "rank2bad-summary" : "rank2heavy-summary")
           << "\",\"heavy_row\":" << heavy_row
           << ",\"sensitive\":" << sensitive.size()
           << ",\"rank1_checked\":" << rank1_checked
           << ",\"pairs\":" << checked << ",\"nonsingular\":"
           << nonsingular << ",\"best\":[" << best_score.over << ','
           << best_score.excess << ',' << best_score.maximum
           << "]}\n" << std::flush;
}

struct SingularReplacement {
    std::uint32_t value = 0;
    std::uint32_t delta = 0;
    std::uint32_t inverse_delta = 0;
    std::uint32_t inverse_delta_A = 0;
    std::uint32_t inverse_delta_A_plus_I = 0;
    std::uint32_t inverse_delta_A_C = 0;
};

void rank2_singular_search(const State& seed, const Matrix& A,
                           const Matrix& A_plus_I, std::ostream& output) {
    const auto TA = multiply(seed.T, A);
    std::vector<int> bad_rows;
    std::uint32_t sensitive_mask = 0;
    for (int row = 0; row < N; ++row) {
        if (feedback_metric(seed, row) > 16) {
            bad_rows.push_back(row);
            sensitive_mask |= seed.T[row] | TA[row];
        }
    }
    if (bad_rows.size() != 3) {
        throw std::runtime_error("rank2 singular expects exactly three bad rows");
    }
    std::vector<int> sensitive;
    for (int bit = 0; bit < N; ++bit) {
        if ((sensitive_mask >> bit) & 1U) sensitive.push_back(bit);
    }

    const auto sparse = sparse_rows();
    std::array<std::vector<SingularReplacement>, N> singular;
    for (const int destination : sensitive) {
        auto& replacements = singular[destination];
        replacements.reserve(sparse.size());
        for (const auto value : sparse) {
            const auto delta = value ^ seed.C[destination];
            if (!delta) continue;
            const auto inverse_delta = apply_row(delta, seed.T);
            // Rank-one determinant is 1+r[d]. We retain exactly the singular
            // replacements; two cross-coupled singular moves can be invertible.
            if (((inverse_delta >> destination) & 1U) == 0) continue;
            const auto inverse_delta_A = apply_row(inverse_delta, A);
            replacements.push_back({
                value,
                delta,
                inverse_delta,
                inverse_delta_A,
                apply_row(inverse_delta, A_plus_I),
                apply_row(inverse_delta_A, seed.C),
            });
        }
    }

    const auto row_metric = [&](int row, int first, int second,
                                const SingularReplacement& left,
                                const SingularReplacement& right) {
        // For singular cross-coupled replacements M=[[0,1],[1,0]], so
        // [T_i[first],T_i[second]]*M^-1 swaps the two coefficients.
        const bool use_left = (seed.T[row] >> second) & 1U;
        const bool use_right = (seed.T[row] >> first) & 1U;
        auto next_TA = TA[row]
                     ^ (use_left ? left.inverse_delta_A : 0)
                     ^ (use_right ? right.inverse_delta_A : 0);
        auto next_B = seed.B[row]
                    ^ (use_left ? left.inverse_delta_A_C : 0)
                    ^ (use_right ? right.inverse_delta_A_C : 0)
                    ^ (((next_TA >> first) & 1U) ? left.delta : 0)
                    ^ (((next_TA >> second) & 1U) ? right.delta : 0);
        const auto next_D = seed.D[row]
                          ^ (use_left ? left.inverse_delta_A_plus_I : 0)
                          ^ (use_right ? right.inverse_delta_A_plus_I : 0);
        return 4 * std::popcount(next_B) + std::popcount(next_D);
    };

    auto best = seed;
    auto best_score = evaluate(seed);
    const int base_output_weight = best_score.output_weight;
    std::uint64_t raw_pairs = 0;
    std::uint64_t cross_coupled = 0;
    std::uint64_t formula_audited = 0;
    std::uint64_t bad_row_prefilter = 0;
    std::uint64_t full_scored = 0;
    for (std::size_t first_index = 0; first_index < sensitive.size(); ++first_index) {
        const int first = sensitive[first_index];
        for (std::size_t second_index = first_index + 1;
             second_index < sensitive.size(); ++second_index) {
            const int second = sensitive[second_index];
            for (const auto& left : singular[first]) {
                for (const auto& right : singular[second]) {
                    ++raw_pairs;
                    if (((left.inverse_delta >> second) & 1U) == 0
                        || ((right.inverse_delta >> first) & 1U) == 0) {
                        continue;
                    }
                    ++cross_coupled;

                    if (formula_audited < 4096) {
                        auto audit_C = seed.C;
                        audit_C[first] = left.value;
                        audit_C[second] = right.value;
                        const auto audit_state = derive(audit_C, A, A_plus_I);
                        for (int row = 0; row < N; ++row) {
                            if (feedback_metric(audit_state, row)
                                != row_metric(row, first, second, left, right)) {
                                throw std::runtime_error("Woodbury row metric mismatch");
                            }
                        }
                        ++formula_audited;
                    }

                    int partial_over = 0;
                    int partial_excess = 0;
                    for (const int row : bad_rows) {
                        const int metric = row_metric(row, first, second, left, right);
                        partial_over += metric > 16;
                        partial_excess += std::max(0, metric - 16);
                    }
                    if (partial_over > best_score.over
                        || (partial_over == best_score.over
                            && partial_excess > best_score.excess)) {
                        continue;
                    }
                    ++bad_row_prefilter;

                    Score score;
                    score.output_weight = base_output_weight
                                        - std::popcount(seed.C[first])
                                        - std::popcount(seed.C[second])
                                        + std::popcount(left.value)
                                        + std::popcount(right.value);
                    bool pruned = false;
                    for (int row = 0; row < N; ++row) {
                        const int metric = row_metric(row, first, second, left, right);
                        const int excess = std::max(0, metric - 16);
                        score.over += metric > 16;
                        score.excess += excess;
                        score.square_excess += excess * excess;
                        score.maximum = std::max(score.maximum, metric);
                        // feedback_weight is filled only for candidates which can
                        // beat the structural prefix; its tie-break cannot alter
                        // an over/excess/maximum improvement.
                        if (score.over > best_score.over
                            || (score.over == best_score.over
                                && score.excess > best_score.excess)) {
                            pruned = true;
                            break;
                        }
                    }
                    if (pruned) continue;
                    ++full_scored;

                    auto C = seed.C;
                    C[first] = left.value;
                    C[second] = right.value;
                    Matrix T{};
                    if (!inverse(C, T)) {
                        throw std::runtime_error("Woodbury cross condition was insufficient");
                    }
                    State candidate;
                    candidate.C = C;
                    candidate.T = T;
                    candidate.B = multiply(multiply(T, A), C);
                    candidate.D = multiply(T, A_plus_I);
                    score = evaluate(candidate);
                    if (score.key() < best_score.key()) {
                        best = candidate;
                        best_score = score;
                        emit(output, "rank2singular", cross_coupled, best, best_score);
                        std::cerr << "rank2singular best pair=" << first << ','
                                  << second << " score=" << best_score.over << '/'
                                  << best_score.excess << '/' << best_score.maximum
                                  << '\n';
                    }
                }
            }
        }
    }
    if (!replay_identity(best, A, A_plus_I)) {
        throw std::runtime_error("rank2 singular identity failed");
    }
    std::cerr << "rank2singular complete sensitive=" << sensitive.size()
              << " raw_pairs=" << raw_pairs
              << " cross_coupled=" << cross_coupled
              << " formula_audited=" << formula_audited
              << " bad_prefilter=" << bad_row_prefilter
              << " full_scored=" << full_scored << " best="
              << best_score.over << '/' << best_score.excess << '/'
              << best_score.maximum << '\n';
    output << "{\"mode\":\"rank2singular-summary\",\"sensitive\":"
           << sensitive.size() << ",\"raw_pairs\":" << raw_pairs
           << ",\"cross_coupled\":" << cross_coupled
           << ",\"formula_audited\":" << formula_audited
           << ",\"bad_row_prefilter\":" << bad_row_prefilter
           << ",\"full_scored\":" << full_scored << ",\"best\":["
           << best_score.over << ',' << best_score.excess << ','
           << best_score.maximum << "]}\n" << std::flush;
}

std::uint32_t random_sparse_row(std::mt19937_64& rng) {
    const int weight_roll = static_cast<int>(rng() % 100);
    const int weight = weight_roll < 10 ? 1 : weight_roll < 40 ? 2 : 3;
    std::uint32_t result = 0;
    while (std::popcount(result) < weight) result |= std::uint32_t{1} << (rng() % N);
    return result;
}

void anneal(const State& seed, std::uint64_t steps, int restarts,
            std::uint64_t random_seed, const Matrix& A,
            const Matrix& A_plus_I, std::ostream& output) {
    std::mt19937_64 rng(random_seed);
    std::uniform_real_distribution<double> unit(0.0, 1.0);
    auto global = seed;
    auto global_score = evaluate(global);
    constexpr std::uint64_t window = 200'000;

    for (int restart = 0; restart < restarts; ++restart) {
        auto current = global;
        auto current_score = global_score;
        for (std::uint64_t step = 1; step <= steps; ++step) {
            const auto in_window = (step - 1) % window;
            if (in_window == 0 && step != 1) {
                current = global;
                current_score = global_score;
            }

            State proposal;
            bool made = false;
            const int destination = static_cast<int>(rng() % N);
            const int kind = static_cast<int>(rng() % 100);
            if (kind < 55) {
                // A sparse row operation is a small, always-invertible move.
                const int source = static_cast<int>(rng() % (N - 1));
                const int adjusted = source >= destination ? source + 1 : source;
                const auto value = current.C[destination] ^ current.C[adjusted];
                if (value && std::popcount(value) <= 3) {
                    made = replace_row(current, destination, value, A, A_plus_I,
                                       proposal);
                }
            } else if (kind < 80) {
                // Two row additions let the walk cross narrow sparse regions.
                int first = static_cast<int>(rng() % N);
                int second = static_cast<int>(rng() % N);
                if (first != destination && second != destination && first != second) {
                    const auto value = current.C[destination]
                                     ^ current.C[first] ^ current.C[second];
                    if (value && std::popcount(value) <= 3) {
                        made = replace_row(current, destination, value, A,
                                           A_plus_I, proposal);
                    }
                }
            } else {
                made = replace_row(current, destination, random_sparse_row(rng),
                                   A, A_plus_I, proposal);
            }
            if (!made) continue;

            const auto proposal_score = evaluate(proposal);
            const double phase = static_cast<double>(in_window) / window;
            const double temperature = 3.0e6 * std::pow(1.0 - phase, 4) + 100.0;
            const double delta = proposal_score.energy() - current_score.energy();
            if (delta <= 0 || unit(rng) < std::exp(-delta / temperature)) {
                current = std::move(proposal);
                current_score = proposal_score;
            }
            if (current_score.key() < global_score.key()) {
                global = current;
                global_score = current_score;
                if (!replay_identity(global, A, A_plus_I)) {
                    throw std::runtime_error("anneal identity failed");
                }
                emit(output, "anneal", static_cast<std::uint64_t>(restart) * steps + step,
                     global, global_score);
                std::cerr << "anneal best restart=" << restart
                          << " step=" << step << " score=" << global_score.over
                          << '/' << global_score.excess << '/'
                          << global_score.maximum << '\n';
                if (global_score.over == 0) return;
            }
        }
    }
}

}  // namespace

int main(int argc, char** argv) {
    const std::string requested_mode = argc > 1 ? argv[1] : "radius2";
    const bool use_over3_seed = requested_mode.ends_with("-over3");
    const bool use_joint_seed = requested_mode.ends_with("-joint");
    const std::string mode = use_over3_seed || use_joint_seed
        ? requested_mode.substr(0, requested_mode.size() - 6)
        : requested_mode;
    const std::uint64_t amount = argc > 2 ? std::stoull(argv[2]) : 1'000'000;
    const int restarts = argc > 3 ? std::stoi(argv[3]) : 4;
    const std::uint64_t random_seed = argc > 4
        ? std::stoull(argv[4], nullptr, 0) : 0x6608C0DEULL;
    const std::string output_path = argc > 5
        ? argv[5] : "sparse-c-66-search.jsonl";

    const auto A = transition();
    auto A_plus_I = A;
    for (int row = 0; row < N; ++row) A_plus_I[row] ^= std::uint32_t{1} << row;
    const bool use_rank1_seed = !use_over3_seed && !use_joint_seed
                             && mode == "anneal";
    const auto start_C = use_over3_seed ? over3_seed_C()
                       : use_joint_seed ? joint_over3_seed_C()
                       : use_rank1_seed ? rank1_seed_C()
                       : structured_seed_C();
    const auto seed = derive(start_C, A, A_plus_I);
    const auto seed_score = evaluate(seed);
    const auto expected = use_over3_seed || use_joint_seed
        ? std::tuple(3, 20, 34, 181, 68)
        : use_rank1_seed
        ? std::tuple(7, 45, 30, 194, 67)
        : std::tuple(8, 38, 30, 193, 68);
    if (std::tuple(seed_score.over, seed_score.excess, seed_score.maximum,
                   seed_score.feedback_weight, seed_score.output_weight)
        != expected) {
        throw std::runtime_error("embedded structured seed does not match audit");
    }

    std::ofstream output(output_path, std::ios::app);
    if (!output) throw std::runtime_error("cannot open output path");
    emit(output, "seed", 0, seed, seed_score);

    if (mode == "radius2") {
        exact_transvection_radius2(seed, A, A_plus_I, output);
    } else if (mode == "rank1") {
        coordinate_descent(seed, static_cast<int>(amount), A, A_plus_I, output);
    } else if (mode == "rank2pool") {
        rank2_pool_search(seed, static_cast<int>(amount), A, A_plus_I, output);
    } else if (mode == "crossmix") {
        crossmix_search(over3_seed_C(), joint_over3_seed_C(), A, A_plus_I,
                        output);
    } else if (mode == "rank2heavy") {
        rank2_heavy_search(seed, A, A_plus_I, output, false);
    } else if (mode == "rank2bad") {
        rank2_heavy_search(seed, A, A_plus_I, output, true);
    } else if (mode == "rank2singular") {
        rank2_singular_search(seed, A, A_plus_I, output);
    } else if (mode == "anneal") {
        anneal(seed, amount, restarts, random_seed, A, A_plus_I, output);
    } else {
        std::cerr << "mode must be radius2, rank1, rank2pool, rank2heavy, rank2bad, "
                     "rank2singular, crossmix, or anneal; "
                     "append -over3 or -joint to select an audited center\n";
        return 2;
    }
    return 0;
}
