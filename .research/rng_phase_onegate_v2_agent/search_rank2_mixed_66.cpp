#define main sparse_c_66_original_main
#include "search_sparse_c_66.cpp"
#undef main

namespace {

void rank2_mixed_search(const State& seed, const Matrix& A,
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
        throw std::runtime_error("rank2 mixed expects exactly three bad rows");
    }
    std::vector<int> sensitive;
    for (int bit = 0; bit < N; ++bit) {
        if ((sensitive_mask >> bit) & 1U) sensitive.push_back(bit);
    }

    const auto sparse = sparse_rows();
    std::array<std::vector<SingularReplacement>, N> singular;
    std::array<std::vector<SingularReplacement>, N> regular;
    for (const int destination : sensitive) {
        for (const auto value : sparse) {
            const auto delta = value ^ seed.C[destination];
            if (!delta) continue;
            const auto inverse_delta = apply_row(delta, seed.T);
            const auto inverse_delta_A = apply_row(inverse_delta, A);
            SingularReplacement replacement{
                value,
                delta,
                inverse_delta,
                inverse_delta_A,
                apply_row(inverse_delta, A_plus_I),
                apply_row(inverse_delta_A, seed.C),
            };
            auto& destination_list = ((inverse_delta >> destination) & 1U)
                ? singular[destination] : regular[destination];
            destination_list.push_back(replacement);
        }
    }

    const auto row_metric = [&](int row, int first, int second,
                                const SingularReplacement& left,
                                const SingularReplacement& right,
                                bool m00, bool m01, bool m10, bool m11) {
        const bool first_coefficient = (seed.T[row] >> first) & 1U;
        const bool second_coefficient = (seed.T[row] >> second) & 1U;
        // M^-1=[[m11,m01],[m10,m00]] over GF(2).
        const bool use_left = (first_coefficient && m11)
                           ^ (second_coefficient && m10);
        const bool use_right = (first_coefficient && m01)
                            ^ (second_coefficient && m00);
        const auto next_TA = TA[row]
                           ^ (use_left ? left.inverse_delta_A : 0)
                           ^ (use_right ? right.inverse_delta_A : 0);
        const auto next_B = seed.B[row]
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
    std::uint64_t jointly_invertible = 0;
    std::uint64_t formula_audited = 0;
    std::uint64_t bad_row_prefilter = 0;
    std::uint64_t full_scored = 0;

    const auto scan_lists = [&](int first, int second,
                                const std::vector<SingularReplacement>& left_list,
                                const std::vector<SingularReplacement>& right_list) {
        for (const auto& left : left_list) {
            for (const auto& right : right_list) {
                ++raw_pairs;
                const bool m00 = 1U ^ ((left.inverse_delta >> first) & 1U);
                const bool m01 = (left.inverse_delta >> second) & 1U;
                const bool m10 = (right.inverse_delta >> first) & 1U;
                const bool m11 = 1U ^ ((right.inverse_delta >> second) & 1U);
                if ((m00 && m11) == (m01 && m10)) continue;
                ++jointly_invertible;

                if (formula_audited < 4096) {
                    auto audit_C = seed.C;
                    audit_C[first] = left.value;
                    audit_C[second] = right.value;
                    const auto audit_state = derive(audit_C, A, A_plus_I);
                    for (int row = 0; row < N; ++row) {
                        if (feedback_metric(audit_state, row)
                            != row_metric(row, first, second, left, right,
                                          m00, m01, m10, m11)) {
                            throw std::runtime_error("mixed Woodbury row mismatch");
                        }
                    }
                    ++formula_audited;
                }

                int partial_over = 0;
                int partial_excess = 0;
                for (const int row : bad_rows) {
                    const int metric = row_metric(row, first, second, left, right,
                                                  m00, m01, m10, m11);
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
                    const int metric = row_metric(row, first, second, left, right,
                                                  m00, m01, m10, m11);
                    const int excess = std::max(0, metric - 16);
                    score.over += metric > 16;
                    score.excess += excess;
                    score.square_excess += excess * excess;
                    score.maximum = std::max(score.maximum, metric);
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
                const auto candidate = derive(C, A, A_plus_I);
                score = evaluate(candidate);
                if (score.key() < best_score.key()) {
                    best = candidate;
                    best_score = score;
                    emit(output, "rank2mixed", jointly_invertible,
                         best, best_score);
                    std::cerr << "rank2mixed best pair=" << first << ',' << second
                              << " score=" << best_score.over << '/'
                              << best_score.excess << '/' << best_score.maximum
                              << '\n';
                }
            }
        }
    };

    for (std::size_t first_index = 0; first_index < sensitive.size(); ++first_index) {
        const int first = sensitive[first_index];
        for (std::size_t second_index = first_index + 1;
             second_index < sensitive.size(); ++second_index) {
            const int second = sensitive[second_index];
            scan_lists(first, second, singular[first], regular[second]);
            scan_lists(first, second, regular[first], singular[second]);
        }
    }

    if (!replay_identity(best, A, A_plus_I)) {
        throw std::runtime_error("rank2 mixed identity failed");
    }
    std::cerr << "rank2mixed complete sensitive=" << sensitive.size()
              << " raw_pairs=" << raw_pairs
              << " jointly_invertible=" << jointly_invertible
              << " formula_audited=" << formula_audited
              << " bad_prefilter=" << bad_row_prefilter
              << " full_scored=" << full_scored << " best="
              << best_score.over << '/' << best_score.excess << '/'
              << best_score.maximum << '\n';
    output << "{\"mode\":\"rank2mixed-summary\",\"sensitive\":"
           << sensitive.size() << ",\"raw_pairs\":" << raw_pairs
           << ",\"jointly_invertible\":" << jointly_invertible
           << ",\"formula_audited\":" << formula_audited
           << ",\"bad_row_prefilter\":" << bad_row_prefilter
           << ",\"full_scored\":" << full_scored << ",\"best\":["
           << best_score.over << ',' << best_score.excess << ','
           << best_score.maximum << "]}\n" << std::flush;
}

}  // namespace

int main(int argc, char** argv) {
    const bool joint = argc > 1 && std::string(argv[1]) == "joint";
    const std::string output_path = argc > 2
        ? argv[2] : joint ? "rank2mixed-joint.jsonl" : "rank2mixed-over3.jsonl";
    const auto A = transition();
    auto A_plus_I = A;
    for (int row = 0; row < N; ++row) A_plus_I[row] ^= std::uint32_t{1} << row;
    const auto seed = derive(joint ? joint_over3_seed_C() : over3_seed_C(),
                             A, A_plus_I);
    const auto score = evaluate(seed);
    if (std::tuple(score.over, score.excess, score.maximum,
                   score.feedback_weight, score.output_weight)
        != std::tuple(3, 20, 34, 181, 68)) {
        throw std::runtime_error("mixed search seed mismatch");
    }
    std::ofstream output(output_path);
    if (!output) throw std::runtime_error("cannot open mixed output");
    emit(output, joint ? "joint-seed" : "over3-seed", 0, seed, score);
    rank2_mixed_search(seed, A, A_plus_I, output);
    return 0;
}
