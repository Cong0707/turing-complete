#define main sparse_search_program_main
#include "sparse_search.cpp"
#undef main

// Exhaust all invertible one- and two-row replacements around a supplied
// sparse T.  Replacement masks are every nonzero 32-bit vector of weight <=2.
// The search streams candidates and retains one best State, so memory is O(1).
int main(int argc, char** argv) {
    if (argc < 2) {
        std::fprintf(stderr, "usage: local_radius2 START.json [OUT.jsonl]\n");
        return 2;
    }
    if (argc > 2 && !std::freopen(argv[2], "w", stdout)) return 2;
    State start;
    if (!load_hex_T(argv[1], start)) {
        std::fprintf(stderr, "could not load start T\n");
        return 2;
    }
    std::vector<std::uint32_t> masks;
    masks.reserve(528);
    for (int a = 0; a < N; ++a) masks.push_back(std::uint32_t{1} << a);
    for (int a = 0; a < N; ++a) for (int b = a + 1; b < N; ++b)
        masks.push_back((std::uint32_t{1} << a) | (std::uint32_t{1} << b));

    State best = start;
    Score best_score = score(best);
    Cover best_cover = greedy_cover(best);
    emit(0, best, best_score, best_cover);
    std::uint64_t first_invertible = 0, second_invertible = 0, evaluated = 0;
    for (int row1 = 0; row1 < N; ++row1) for (auto mask1 : masks) {
        if (mask1 == start.T[row1]) continue;
        Matrix t1 = start.T;
        t1[row1] = mask1;
        State one;
        if (!from_T(t1, one)) continue;
        ++first_invertible;
        const auto one_score = score(one);
        if (score_key(one_score) < score_key(best_score)) {
            best = one; best_score = one_score; best_cover = greedy_cover(best);
            emit(first_invertible, best, best_score, best_cover);
        }
        for (int row2 = 0; row2 < N; ++row2) for (auto mask2 : masks) {
            if (mask2 == one.T[row2]) continue;
            Matrix t2 = one.T;
            t2[row2] = mask2;
            State two;
            ++evaluated;
            if (!from_T(t2, two)) continue;
            ++second_invertible;
            const auto two_score = score(two);
            if (score_key(two_score) < score_key(best_score)) {
                best = two; best_score = two_score; best_cover = greedy_cover(best);
                emit(evaluated, best, best_score, best_cover);
                std::fprintf(stderr,
                    "best eval=%llu bad=%d linear_excess=%d squared_excess=%d max=%d total=%d t2=%d xor=%d\n",
                    (unsigned long long)evaluated, best_score.bad, best_score.excess,
                    best_score.sq, best_score.maxw, best_score.total, best_score.t2, best_cover.xor_count);
            }
        }
    }
    std::fprintf(stderr,
        "summary first_invertible=%llu evaluated=%llu second_invertible=%llu best_bad=%d best_linear_excess=%d best_squared_excess=%d best_max=%d best_total=%d best_t2=%d best_xor=%d\n",
        (unsigned long long)first_invertible, (unsigned long long)evaluated,
        (unsigned long long)second_invertible, best_score.bad, best_score.excess,
        best_score.sq, best_score.maxw, best_score.total, best_score.t2, best_cover.xor_count);
    return 0;
}
