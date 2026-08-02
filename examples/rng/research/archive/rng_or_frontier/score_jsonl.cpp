#define main rng_basis_walk_main
#include "../rng_basis_search_v2/walk.cpp"
#undef main

#include <cinttypes>
#include <fstream>
#include <sstream>

namespace {

bool parse_matrix(const std::string& line, const char* key, Matrix& matrix) {
    const std::string marker = std::string("\"") + key + "\":[";
    std::size_t cursor = line.find(marker);
    if (cursor == std::string::npos) {
        return false;
    }
    cursor += marker.size();
    for (int index = 0; index < kBits; ++index) {
        cursor = line.find('"', cursor);
        if (cursor == std::string::npos || cursor + 9 >= line.size()) {
            return false;
        }
        char* end = nullptr;
        matrix[index] = static_cast<std::uint32_t>(
            std::strtoul(line.c_str() + cursor + 1, &end, 16));
        if (end != line.c_str() + cursor + 9) {
            return false;
        }
        cursor = static_cast<std::size_t>(end - line.c_str()) + 1;
    }
    return true;
}

}  // namespace

int main(int argc, char** argv) {
    if (argc < 4) {
        std::fprintf(stderr,
                     "usage: score_jsonl INPUT SELECTED_JSONL SUMMARY_CSV [MAX_PENALTY]\n");
        return 2;
    }
    const int maximum_penalty = argc > 4 ? std::atoi(argv[4]) : 5;
    std::ifstream input(argv[1]);
    std::ofstream selected(argv[2]);
    std::ofstream summary(argv[3]);
    if (!input || !selected || !summary) {
        std::fprintf(stderr, "cannot open input/output\n");
        return 2;
    }
    summary << "line,xor,penalty,greedy_or,budget\n";

    std::string line;
    std::uint64_t line_number = 0;
    std::uint64_t kept = 0;
    std::array<std::uint64_t, 65> feasible_by_xor{};
    int best_budget = 1000;
    while (std::getline(input, line)) {
        ++line_number;
        State state;
        if (!parse_matrix(line, "T", state.T) ||
            !parse_matrix(line, "B", state.B) ||
            !parse_matrix(line, "C", state.C)) {
            std::fprintf(stderr, "parse failure at line %" PRIu64 "\n", line_number);
            return 2;
        }
        const auto cover = greedy_cover(state);
        const auto mode = mode_score(state, cover);
        const int budget = mode.feasible()
            ? 3 * cover.greedy_xor + mode.greedy_or
            : 1000;
        if (mode.feasible()) {
            ++feasible_by_xor[cover.greedy_xor];
            best_budget = std::min(best_budget, budget);
        }
        if (mode.feasible() || mode.penalty <= maximum_penalty) {
            selected << line << '\n';
            summary << line_number << ',' << cover.greedy_xor << ','
                    << mode.penalty << ',' << mode.greedy_or << ',' << budget << '\n';
            ++kept;
        }
        if (budget <= 221) {
            std::fprintf(stderr,
                         "TARGET line=%" PRIu64 " xor=%d or=%d budget=%d\n",
                         line_number, cover.greedy_xor, mode.greedy_or, budget);
            std::fflush(stderr);
        }
        if (line_number % 5000 == 0) {
            std::fprintf(stderr, "scored=%" PRIu64 " kept=%" PRIu64
                                 " best_budget=%d\n",
                         line_number, kept, best_budget);
            std::fflush(stderr);
        }
    }
    std::fprintf(stderr, "done scored=%" PRIu64 " kept=%" PRIu64
                         " best_budget=%d",
                 line_number, kept, best_budget);
    for (int xor_count = 0; xor_count <= 64; ++xor_count) {
        if (feasible_by_xor[xor_count]) {
            std::fprintf(stderr, " feasible_x%d=%" PRIu64,
                         xor_count, feasible_by_xor[xor_count]);
        }
    }
    std::fprintf(stderr, "\n");
    return 0;
}
