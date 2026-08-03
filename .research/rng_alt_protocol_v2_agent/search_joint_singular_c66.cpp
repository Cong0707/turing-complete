#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <queue>
#include <stdexcept>
#include <string>
#include <tuple>
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

Matrix load_last_c(const std::string& path) {
    std::ifstream input(path);
    if (!input) throw std::runtime_error("cannot open center JSONL");
    Matrix result{};
    bool found = false;
    std::string line;
    while (std::getline(input, line)) {
        Matrix parsed{};
        if (parse_matrix(line, "C", parsed)) {
            result = parsed;
            found = true;
        }
    }
    if (!found) throw std::runtime_error("center JSONL contains no C matrix");
    return result;
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

struct Score {
    int over = 0;
    int excess = 0;
    int maximum = 0;
    int combined_weight = 0;

    auto key() const {
        return std::tuple(over, excess, maximum, combined_weight);
    }
};

Score evaluate(const Matrix& b, const Matrix& t) {
    Score result;
    for (int row = 0; row < N; ++row) {
        const int metric = 4 * std::popcount(b[row]) + std::popcount(t[row]);
        result.over += metric > 16;
        result.excess += std::max(0, metric - 16);
        result.maximum = std::max(result.maximum, metric);
        result.combined_weight += std::popcount(b[row]) + std::popcount(t[row]);
    }
    return result;
}

struct Replacement {
    std::uint32_t value = 0;
    std::uint32_t delta = 0;
    std::uint32_t alpha = 0;
    std::uint32_t a_alpha = 0;
    std::uint32_t t_alpha = 0;
    std::uint32_t b_alpha = 0;
    std::uint8_t distance = 0;
};

void emit_matrix(std::ostream& output, const char* name, const Matrix& matrix) {
    output << "\"" << name << "\":[";
    for (int row = 0; row < N; ++row) {
        output << (row ? ",\"" : "\"") << std::hex << std::setw(8)
               << std::setfill('0') << matrix[row] << "\"";
    }
    output << std::dec << ']';
}

void emit_solution(std::ostream& output, int first, int second,
                   std::uint64_t checked, const Score& score,
                   const Matrix& c, const Matrix& p,
                   const Matrix& b, const Matrix& t, int third = -1) {
    output << "{\"status\":\"sat\",\"rows\":[" << first << ',' << second
           << (third >= 0 ? "," + std::to_string(third) : std::string{})
           << "],\"checked\":" << checked << ",\"score\":{\"over\":"
           << score.over << ",\"excess\":" << score.excess
           << ",\"max\":" << score.maximum << ",\"combined_weight\":"
           << score.combined_weight << "},";
    emit_matrix(output, "C", c); output << ',';
    emit_matrix(output, "P", p); output << ',';
    emit_matrix(output, "B", b); output << ',';
    emit_matrix(output, "T", t);
    output << "}\n";
}

struct PairChoice {
    int first_row = 0;
    int second_row = 0;
    std::uint32_t first_value = 0;
    std::uint32_t second_value = 0;
    int bad_over = 0;
    int bad_excess = 0;
    int bad_maximum = 0;
    int bad_sum = 0;
    int distance = 0;
    int third_row = -1;

    auto key() const {
        return std::tuple(bad_over, bad_excess, bad_maximum, bad_sum,
                          distance, third_row, first_value, second_value);
    }
};

struct PairChoiceBetter {
    bool operator()(const PairChoice& left, const PairChoice& right) const {
        return left.key() < right.key();
    }
};

using PairHeap = std::priority_queue<PairChoice, std::vector<PairChoice>,
                                     PairChoiceBetter>;

}  // namespace

int main(int argc, char** argv) {
    if (argc < 3) {
        std::cerr << "usage: search_joint_singular_c66 CENTER.jsonl OUTPUT.jsonl "
                     "[MAX_HAMMING] [BEAM_PER_DESTINATION]\n";
        return 4;
    }
    const int max_hamming = argc > 3 ? std::stoi(argv[3]) : 8;
    const std::size_t pair_beam_per_destination = argc > 4
        ? std::stoull(argv[4]) : 64;
    const auto A = transition();
    auto A_plus_I = A;
    for (int bit = 0; bit < N; ++bit) A_plus_I[bit] ^= std::uint32_t{1} << bit;
    const auto C = load_last_c(argv[1]);
    Matrix P{};
    if (!inverse(C, P)) throw std::runtime_error("center C is singular");
    const auto PA = multiply(P, A);
    const auto B = multiply(PA, C);
    const auto T = multiply(P, A_plus_I);
    const auto base_score = evaluate(B, T);

    std::vector<int> bad_rows;
    for (int row = 0; row < N; ++row) {
        if (4 * std::popcount(B[row]) + std::popcount(T[row]) > 16) {
            bad_rows.push_back(row);
        }
    }
    if (bad_rows.empty()) {
        std::cerr << "center is already feasible\n";
        return 0;
    }
    if (bad_rows.size() > 3) {
        throw std::runtime_error("rank-3 beam expects at most three bad rows");
    }

    Matrix a_columns{};
    for (int column = 0; column < N; ++column) {
        for (int row = 0; row < N; ++row) {
            a_columns[column] |= ((A[row] >> column) & 1U) << row;
        }
    }

    std::vector<std::pair<int, int>> destinations;
    for (int first = 0; first < N; ++first) {
        for (int second = first + 1; second < N; ++second) {
            std::uint32_t completion =
                std::numeric_limits<std::uint32_t>::max();
            for (const int row : bad_rows) {
                const auto sensitive = P[row] | PA[row];
                if (((sensitive >> first) & 1U) == 0
                    && ((sensitive >> second) & 1U) == 0) {
                    completion &= sensitive;
                }
            }
            completion &= ~(std::uint32_t{1} << first);
            completion &= ~(std::uint32_t{1} << second);
            if (completion) destinations.emplace_back(first, second);
        }
    }

    const auto values = sparse_rows();
    std::ofstream output(argv[2], std::ios::app);
    if (!output) throw std::runtime_error("cannot open output JSONL");
    std::uint64_t checked = 0;
    std::uint64_t within_radius = 0;
    std::uint64_t nonsingular = 0;
    std::uint64_t repaired_original = 0;
    std::uint64_t pair_with_possible_third = 0;
    std::uint64_t pair_destination_options = 0;
    auto best_score = base_score;
    std::vector<PairChoice> pair_beam;
    constexpr std::size_t pair_beam_per_mask = 64;

    for (const auto [first_row, second_row] : destinations) {
        std::array<PairHeap, 8> local_pair_beam;
        std::array<PairHeap, N> local_destination_beam;
        std::vector<Replacement> first_values;
        std::vector<Replacement> second_values;
        const auto build = [&](int row, std::vector<Replacement>& result) {
            result.reserve(values.size());
            for (const auto value : values) {
                const auto delta = value ^ C[row];
                const auto distance = std::popcount(delta);
                if (distance == 0 || distance > max_hamming) continue;
                const auto alpha = apply_row(delta, P);
                const auto a_alpha = apply_row(alpha, A);
                result.push_back({value, delta, alpha, a_alpha,
                    apply_row(alpha, A_plus_I), apply_row(a_alpha, C),
                    static_cast<std::uint8_t>(distance)});
            }
        };
        build(first_row, first_values);
        build(second_row, second_values);

        for (const auto& first : first_values) {
            for (const auto& second : second_values) {
                ++checked;
                if (first.distance + second.distance > max_hamming) continue;
                ++within_radius;

                const bool m00 = true ^ ((first.alpha >> first_row) & 1U);
                const bool m01 = (first.alpha >> second_row) & 1U;
                const bool m10 = (second.alpha >> first_row) & 1U;
                const bool m11 = true ^ ((second.alpha >> second_row) & 1U);
                if ((m00 && m11) == (m01 && m10)) continue;
                ++nonsingular;

                Matrix candidate_b{};
                Matrix candidate_t{};
                int bad_mask = 0;
                int bad_excess = 0;
                int bad_maximum = 0;
                int bad_sum = 0;
                for (int bad_index = 0;
                     bad_index < static_cast<int>(bad_rows.size()); ++bad_index) {
                    const int row = bad_rows[bad_index];
                    const bool x0 = (P[row] >> first_row) & 1U;
                    const bool x1 = (P[row] >> second_row) & 1U;
                    const bool y0 = (x0 && m11) ^ (x1 && m10);
                    const bool y1 = (x0 && m01) ^ (x1 && m00);
                    const auto p_row = P[row]
                                     ^ (y0 ? first.alpha : 0)
                                     ^ (y1 ? second.alpha : 0);
                    const bool z0 = std::popcount(p_row & a_columns[first_row]) & 1U;
                    const bool z1 = std::popcount(p_row & a_columns[second_row]) & 1U;
                    candidate_t[row] = T[row]
                                     ^ (y0 ? first.t_alpha : 0)
                                     ^ (y1 ? second.t_alpha : 0);
                    candidate_b[row] = B[row]
                                     ^ (y0 ? first.b_alpha : 0)
                                     ^ (y1 ? second.b_alpha : 0)
                                     ^ (z0 ? first.delta : 0)
                                     ^ (z1 ? second.delta : 0);
                    const int metric = 4 * std::popcount(candidate_b[row])
                                     + std::popcount(candidate_t[row]);
                    bad_mask |= (metric > 16) << bad_index;
                    bad_excess += std::max(0, metric - 16);
                    bad_maximum = std::max(bad_maximum, metric);
                    bad_sum += metric;
                }

                Matrix candidate_p{};
                Matrix candidate_pa{};
                std::uint32_t possible_third =
                    std::numeric_limits<std::uint32_t>::max();
                for (int row = 0; row < N; ++row) {
                    const bool x0 = (P[row] >> first_row) & 1U;
                    const bool x1 = (P[row] >> second_row) & 1U;
                    const bool y0 = (x0 && m11) ^ (x1 && m10);
                    const bool y1 = (x0 && m01) ^ (x1 && m00);
                    candidate_p[row] = P[row]
                                     ^ (y0 ? first.alpha : 0)
                                     ^ (y1 ? second.alpha : 0);
                    candidate_pa[row] = PA[row]
                                      ^ (y0 ? first.a_alpha : 0)
                                      ^ (y1 ? second.a_alpha : 0);
                    const bool z0 = (candidate_pa[row] >> first_row) & 1U;
                    const bool z1 = (candidate_pa[row] >> second_row) & 1U;
                    candidate_t[row] = T[row]
                                     ^ (y0 ? first.t_alpha : 0)
                                     ^ (y1 ? second.t_alpha : 0);
                    candidate_b[row] = B[row]
                                     ^ (y0 ? first.b_alpha : 0)
                                     ^ (y1 ? second.b_alpha : 0)
                                     ^ (z0 ? first.delta : 0)
                                     ^ (z1 ? second.delta : 0);
                    const int metric = 4 * std::popcount(candidate_b[row])
                                     + std::popcount(candidate_t[row]);
                    if (metric > 16) {
                        possible_third &= candidate_p[row] | candidate_pa[row];
                    }
                }
                possible_third &= ~(std::uint32_t{1} << first_row);
                possible_third &= ~(std::uint32_t{1} << second_row);
                const auto pair_score = evaluate(candidate_b, candidate_t);
                if (possible_third) {
                    ++pair_with_possible_third;
                    pair_destination_options += std::popcount(possible_third);
                }
                auto remaining_destinations = possible_third;
                while (remaining_destinations) {
                    const int third = std::countr_zero(remaining_destinations);
                    remaining_destinations &= remaining_destinations - 1;
                    PairChoice choice{first_row, second_row, first.value,
                                      second.value, pair_score.over,
                                      pair_score.excess, pair_score.maximum,
                                      pair_score.combined_weight,
                                      first.distance + second.distance, third};
                    auto& heap = local_destination_beam[third];
                    if (heap.size() < pair_beam_per_destination) {
                        heap.push(choice);
                    } else if (choice.key() < heap.top().key()) {
                        heap.pop();
                        heap.push(choice);
                    }
                }
                if (bad_mask != 0) {
                    PairChoice choice{first_row, second_row, first.value,
                                      second.value, std::popcount(
                                          static_cast<unsigned>(bad_mask)),
                                      bad_excess, bad_maximum, bad_sum,
                                      first.distance + second.distance, -1};
                    auto& heap = local_pair_beam[bad_mask];
                    if (heap.size() < pair_beam_per_mask) {
                        heap.push(choice);
                    } else if (choice.key() < heap.top().key()) {
                        heap.pop();
                        heap.push(choice);
                    }
                    continue;
                }
                ++repaired_original;

                for (int row = 0; row < N; ++row) {
                    if (candidate_b[row] || candidate_t[row]) continue;
                    const bool x0 = (P[row] >> first_row) & 1U;
                    const bool x1 = (P[row] >> second_row) & 1U;
                    const bool y0 = (x0 && m11) ^ (x1 && m10);
                    const bool y1 = (x0 && m01) ^ (x1 && m00);
                    const auto p_row = P[row]
                                     ^ (y0 ? first.alpha : 0)
                                     ^ (y1 ? second.alpha : 0);
                    const bool z0 = std::popcount(p_row & a_columns[first_row]) & 1U;
                    const bool z1 = std::popcount(p_row & a_columns[second_row]) & 1U;
                    candidate_t[row] = T[row]
                                     ^ (y0 ? first.t_alpha : 0)
                                     ^ (y1 ? second.t_alpha : 0);
                    candidate_b[row] = B[row]
                                     ^ (y0 ? first.b_alpha : 0)
                                     ^ (y1 ? second.b_alpha : 0)
                                     ^ (z0 ? first.delta : 0)
                                     ^ (z1 ? second.delta : 0);
                }
                const auto score = evaluate(candidate_b, candidate_t);
                if (score.key() < best_score.key()) {
                    auto candidate_c = C;
                    candidate_c[first_row] = first.value;
                    candidate_c[second_row] = second.value;
                    Matrix candidate_p{};
                    if (!inverse(candidate_c, candidate_p)) {
                        throw std::runtime_error("rank-2 determinant mismatch");
                    }
                    const auto verified_t = multiply(candidate_p, A_plus_I);
                    const auto verified_b = multiply(multiply(candidate_p, A), candidate_c);
                    if (verified_t != candidate_t || verified_b != candidate_b) {
                        throw std::runtime_error("rank-2 update identity mismatch");
                    }
                    best_score = score;
                    emit_solution(output, first_row, second_row, checked, score,
                                  candidate_c, candidate_p, candidate_b, candidate_t);
                    std::cerr << "best rows=" << first_row << ',' << second_row
                              << " checked=" << checked << " score="
                              << score.over << '/' << score.excess << '/'
                              << score.maximum << '\n';
                    if (score.over == 0) return 0;
                }
            }
        }
        for (auto& heap : local_pair_beam) {
            while (!heap.empty()) {
                pair_beam.push_back(heap.top());
                heap.pop();
            }
        }
        for (auto& heap : local_destination_beam) {
            while (!heap.empty()) {
                pair_beam.push_back(heap.top());
                heap.pop();
            }
        }
        std::cerr << "pair " << first_row << ',' << second_row
                  << " checked=" << checked << " radius=" << within_radius
                  << " invertible=" << nonsingular
                  << " repaired=" << repaired_original << '\n';
    }

    std::uint64_t rank3_checked = 0;
    std::uint64_t rank3_nonsingular = 0;
    std::uint64_t rank3_repaired = 0;
    std::uint64_t rank3_empty_intersection = 0;
    for (const auto& pair : pair_beam) {
        auto pair_c = C;
        pair_c[pair.first_row] = pair.first_value;
        pair_c[pair.second_row] = pair.second_value;
        Matrix pair_p{};
        if (!inverse(pair_c, pair_p)) {
            throw std::runtime_error("stored pair became singular");
        }
        const auto pair_pa = multiply(pair_p, A);
        const auto pair_b = multiply(pair_pa, pair_c);
        const auto pair_t = multiply(pair_p, A_plus_I);
        std::vector<int> pair_bad_rows;
        std::uint32_t possible_destinations =
            std::numeric_limits<std::uint32_t>::max();
        for (int row = 0; row < N; ++row) {
            const int metric = 4 * std::popcount(pair_b[row])
                             + std::popcount(pair_t[row]);
            if (metric > 16) {
                pair_bad_rows.push_back(row);
                possible_destinations &= pair_p[row] | pair_pa[row];
            }
        }
        possible_destinations &= ~(std::uint32_t{1} << pair.first_row);
        possible_destinations &= ~(std::uint32_t{1} << pair.second_row);
        if (pair.third_row >= 0) {
            possible_destinations &= std::uint32_t{1} << pair.third_row;
        }
        if (possible_destinations == 0) {
            ++rank3_empty_intersection;
            continue;
        }

        while (possible_destinations) {
            const int destination = std::countr_zero(possible_destinations);
            possible_destinations &= possible_destinations - 1;
            for (const auto value : values) {
                ++rank3_checked;
                const auto delta = value ^ pair_c[destination];
                if (delta == 0) continue;
                const auto alpha = apply_row(delta, pair_p);
                if ((alpha >> destination) & 1U) continue;
                ++rank3_nonsingular;
                const auto t_alpha = apply_row(alpha, A_plus_I);
                const auto b_alpha = apply_row(apply_row(alpha, A), pair_c);

                bool repaired = true;
                for (const int row : pair_bad_rows) {
                    const bool x = (pair_p[row] >> destination) & 1U;
                    const auto p_row = pair_p[row] ^ (x ? alpha : 0);
                    const bool z = std::popcount(
                        p_row & a_columns[destination]) & 1U;
                    const auto t_row = pair_t[row] ^ (x ? t_alpha : 0);
                    const auto b_row = pair_b[row] ^ (x ? b_alpha : 0)
                                     ^ (z ? delta : 0);
                    if (4 * std::popcount(b_row) + std::popcount(t_row) > 16) {
                        repaired = false;
                        break;
                    }
                }
                if (!repaired) continue;
                ++rank3_repaired;

                Matrix candidate_b{};
                Matrix candidate_t{};
                Matrix candidate_p{};
                for (int row = 0; row < N; ++row) {
                    const bool x = (pair_p[row] >> destination) & 1U;
                    candidate_p[row] = pair_p[row] ^ (x ? alpha : 0);
                    const bool z = std::popcount(
                        candidate_p[row] & a_columns[destination]) & 1U;
                    candidate_t[row] = pair_t[row] ^ (x ? t_alpha : 0);
                    candidate_b[row] = pair_b[row] ^ (x ? b_alpha : 0)
                                     ^ (z ? delta : 0);
                }
                const auto score = evaluate(candidate_b, candidate_t);
                if (score.key() >= best_score.key()) continue;
                auto candidate_c = pair_c;
                candidate_c[destination] = value;
                Matrix verified_p{};
                if (!inverse(candidate_c, verified_p)) {
                    throw std::runtime_error("rank-3 inverse update mismatch");
                }
                const auto verified_t = multiply(verified_p, A_plus_I);
                const auto verified_b = multiply(multiply(verified_p, A), candidate_c);
                if (verified_p != candidate_p || verified_t != candidate_t
                    || verified_b != candidate_b) {
                    throw std::runtime_error("rank-3 update identity mismatch");
                }
                best_score = score;
                emit_solution(output, pair.first_row, pair.second_row,
                              rank3_checked, score, candidate_c, candidate_p,
                              candidate_b, candidate_t, destination);
                std::cerr << "rank3 best rows=" << pair.first_row << ','
                          << pair.second_row << ',' << destination
                          << " checked=" << rank3_checked << " score="
                          << score.over << '/' << score.excess << '/'
                          << score.maximum << '\n';
                if (score.over == 0) return 0;
            }
        }
    }

    output << "{\"status\":\"unsat-in-subspace\",\"max_hamming\":"
           << max_hamming << ",\"destination_pairs\":" << destinations.size()
           << ",\"checked\":" << checked << ",\"within_radius\":"
           << within_radius << ",\"invertible\":" << nonsingular
           << ",\"repaired_original\":" << repaired_original
           << ",\"pair_with_possible_third\":" << pair_with_possible_third
           << ",\"pair_destination_options\":" << pair_destination_options
           << ",\"pair_beam\":" << pair_beam.size()
           << ",\"rank3_checked\":" << rank3_checked
           << ",\"rank3_invertible\":" << rank3_nonsingular
           << ",\"rank3_repaired\":" << rank3_repaired
           << ",\"rank3_empty_intersection\":" << rank3_empty_intersection
           << ",\"best\":[" << best_score.over << ',' << best_score.excess
           << ',' << best_score.maximum << "]}\n";
    std::cerr << "complete pairs=" << destinations.size() << " checked=" << checked
              << " radius=" << within_radius << " invertible=" << nonsingular
              << " repaired=" << repaired_original << " best="
              << best_score.over << '/' << best_score.excess << '/'
              << best_score.maximum << '\n';
    return 2;
}
