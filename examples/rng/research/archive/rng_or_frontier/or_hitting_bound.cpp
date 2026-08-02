#define main rng_basis_walk_main
#include "../rng_basis_search_v2/walk.cpp"
#undef main

#include <cinttypes>
#include <fstream>
#include <unordered_map>

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
        if (cursor == std::string::npos) {
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

int hitting_number(const std::vector<std::uint32_t>& raw_family) {
    std::vector<std::uint32_t> family;
    for (const auto support : raw_family) {
        if (support == 0) {
            return 1000;
        }
        if (std::find(family.begin(), family.end(), support) == family.end()) {
            family.push_back(support);
        }
    }
    // If A is a subset of B, hitting A already hits B; retain only minimal sets.
    std::vector<std::uint32_t> minimal;
    for (const auto candidate : family) {
        const bool has_strict_subset = std::any_of(
            family.begin(), family.end(), [&](std::uint32_t other) {
                return other != candidate && (other & candidate) == other;
            });
        if (!has_strict_subset) {
            minimal.push_back(candidate);
        }
    }
    family = std::move(minimal);
    if (family.empty()) {
        return 0;
    }
    if (family.size() > 63) {
        return 1000;
    }

    const std::uint64_t all = (std::uint64_t{1} << family.size()) - 1;
    std::array<std::uint64_t, kBits> covers{};
    for (std::size_t index = 0; index < family.size(); ++index) {
        for (int state = 0; state < kBits; ++state) {
            if ((family[index] >> state) & 1U) {
                covers[state] |= std::uint64_t{1} << index;
            }
        }
    }
    std::unordered_map<std::uint64_t, int> memo;
    const auto solve = [&](auto&& self, std::uint64_t covered) -> int {
        if (covered == all) {
            return 0;
        }
        const auto found = memo.find(covered);
        if (found != memo.end()) {
            return found->second;
        }
        int chosen = -1;
        int chosen_weight = 1000;
        for (std::size_t index = 0; index < family.size(); ++index) {
            if ((covered >> index) & 1U) {
                continue;
            }
            const int weight = std::popcount(family[index]);
            if (weight < chosen_weight) {
                chosen = static_cast<int>(index);
                chosen_weight = weight;
            }
        }
        int best = 1000;
        for (std::uint32_t states = family[chosen]; states; states &= states - 1) {
            const int state = std::countr_zero(states);
            best = std::min(best, 1 + self(self, covered | covers[state]));
        }
        memo.emplace(covered, best);
        return best;
    };
    return solve(solve, 0);
}

int mode_hitting_lower_bound(const State& state, int minimum_feedback_weight) {
    int result = 0;
    for (int seed = 0; seed < kBits; ++seed) {
        std::vector<std::uint32_t> family;
        for (int output = 0; output < kBits; ++output) {
            if ((state.T[output] >> seed) & 1U &&
                std::popcount(state.B[output]) >= minimum_feedback_weight) {
                family.push_back(state.B[output]);
            }
        }
        result += hitting_number(family);
    }
    return result;
}

}  // namespace

int main(int argc, char** argv) {
    if (argc < 3) {
        std::fprintf(stderr, "usage: or_hitting_bound INPUT CANDIDATES_CSV\n");
        return 2;
    }
    std::ifstream input(argv[1]);
    std::ofstream candidates(argv[2]);
    if (!input || !candidates) {
        return 2;
    }
    candidates << "line,xor,or_lower_bound,heavy_or_lower_bound,target_or\n";
    std::array<int, 65> minimum;
    minimum.fill(1000);
    std::array<std::uint64_t, 65> minimum_count{};
    std::array<std::uint64_t, 65> minimum_line{};
    std::array<std::uint64_t, 65> within_target{};
    std::array<int, 65> heavy_minimum;
    heavy_minimum.fill(1000);
    std::array<std::uint64_t, 65> heavy_minimum_line{};

    std::string line;
    std::uint64_t line_number = 0;
    while (std::getline(input, line)) {
        ++line_number;
        State state;
        if (!parse_matrix(line, "T", state.T) ||
            !parse_matrix(line, "B", state.B) ||
            !parse_matrix(line, "C", state.C)) {
            std::fprintf(stderr, "parse failure at line %" PRIu64 "\n", line_number);
            return 2;
        }
        const int xor_count = greedy_cover(state).greedy_xor;
        const int lower = mode_hitting_lower_bound(state, 1);
        const int heavy_lower = mode_hitting_lower_bound(state, 3);
        if (lower < minimum[xor_count]) {
            minimum[xor_count] = lower;
            minimum_count[xor_count] = 1;
            minimum_line[xor_count] = line_number;
        } else if (lower == minimum[xor_count]) {
            ++minimum_count[xor_count];
        }
        if (heavy_lower < heavy_minimum[xor_count]) {
            heavy_minimum[xor_count] = heavy_lower;
            heavy_minimum_line[xor_count] = line_number;
        }
        const int target_or = 221 - 3 * xor_count;
        if (heavy_lower <= target_or) {
            ++within_target[xor_count];
            candidates << line_number << ',' << xor_count << ',' << lower << ','
                       << heavy_lower
                       << ',' << target_or << '\n';
        }
    }
    std::fprintf(stderr, "scanned=%" PRIu64, line_number);
    for (int xor_count = 0; xor_count <= 64; ++xor_count) {
        if (minimum[xor_count] != 1000) {
            std::fprintf(stderr,
                         " x%d_min=%d(line=%" PRIu64 ",count=%" PRIu64
                         ",heavy_min=%d@%" PRIu64 ",target_hits=%" PRIu64 ")",
                         xor_count, minimum[xor_count], minimum_line[xor_count],
                         minimum_count[xor_count], heavy_minimum[xor_count],
                         heavy_minimum_line[xor_count],
                         within_target[xor_count]);
        }
    }
    std::fprintf(stderr, "\n");
    return 0;
}
