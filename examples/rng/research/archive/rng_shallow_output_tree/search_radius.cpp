#include <algorithm>
#include <array>
#include <bit>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <functional>
#include <numeric>
#include <queue>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

#ifdef _WIN32
#include <windows.h>
#include <psapi.h>
#endif

constexpr int N = 32;
constexpr int GROUND = N;
using Matrix = std::array<std::uint32_t, N>;
using Edge = std::pair<int, int>;

static std::uint32_t apply_row(std::uint32_t row, const Matrix& matrix) {
    std::uint32_t result = 0;
    while (row) {
        const int bit = std::countr_zero(row);
        result ^= matrix[bit];
        row &= row - 1;
    }
    return result;
}

static Matrix multiply(const Matrix& left, const Matrix& right) {
    Matrix result{};
    for (int row = 0; row < N; ++row) result[row] = apply_row(left[row], right);
    return result;
}

static Matrix identity() {
    Matrix result{};
    for (int bit = 0; bit < N; ++bit) result[bit] = std::uint32_t{1} << bit;
    return result;
}

static Matrix transition_matrix() {
    Matrix result{};
    for (int source = 0; source < N; ++source) {
        std::uint32_t value = std::uint32_t{1} << source;
        value ^= value >> 13;
        value ^= value << 17;
        value ^= value >> 5;
        for (int output = 0; output < N; ++output) {
            result[output] |= ((value >> output) & 1U) << source;
        }
    }
    return result;
}

static bool invert_checked(Matrix rows, Matrix& inverse) {
    inverse = identity();
    for (int column = 0; column < N; ++column) {
        int pivot = column;
        while (pivot < N && !(rows[pivot] & (std::uint32_t{1} << column))) ++pivot;
        if (pivot == N) return false;
        std::swap(rows[pivot], rows[column]);
        std::swap(inverse[pivot], inverse[column]);
        for (int row = 0; row < N; ++row) {
            if (row != column && (rows[row] & (std::uint32_t{1} << column))) {
                rows[row] ^= rows[column];
                inverse[row] ^= inverse[column];
            }
        }
    }
    return true;
}

struct State {
    Matrix C{};
    Matrix T{};
    Matrix B{};
};

static bool from_C(const Matrix& C, State& state) {
    Matrix inverse;
    if (!invert_checked(C, inverse)) return false;
    state.C = C;
    state.T = multiply(inverse, transition_matrix());
    state.B = multiply(state.T, C);
    return true;
}

static bool load_C(const char* path, Matrix& C) {
    std::ifstream stream(path);
    if (!stream) return false;
    std::string line;
    std::string last;
    while (std::getline(stream, line)) {
        if (line.find("\"C\"") != std::string::npos) last = line;
    }
    const auto marker = last.find("\"C\"");
    const auto open = marker == std::string::npos ? marker : last.find('[', marker);
    if (open == std::string::npos) return false;
    std::size_t cursor = open + 1;
    for (int row = 0; row < N; ++row) {
        const auto quote = last.find('"', cursor);
        const auto end = quote == std::string::npos ? quote : last.find('"', quote + 1);
        if (end == std::string::npos) return false;
        C[row] = static_cast<std::uint32_t>(std::strtoull(
            last.substr(quote + 1, end - quote - 1).c_str(), nullptr, 16));
        cursor = end + 1;
    }
    return true;
}

static Edge edge_from_row(std::uint32_t row) {
    const int first = std::countr_zero(row);
    row &= row - 1;
    if (!row) return {first, GROUND};
    const int second = std::countr_zero(row);
    row &= row - 1;
    if (row) std::abort();
    return {first, second};
}

static std::uint32_t row_from_edge(Edge edge) {
    std::uint32_t result = 0;
    if (edge.first != GROUND) result ^= std::uint32_t{1} << edge.first;
    if (edge.second != GROUND) result ^= std::uint32_t{1} << edge.second;
    return result;
}

struct Dsu {
    std::array<int, N + 1> parent{};
    Dsu() { std::iota(parent.begin(), parent.end(), 0); }
    int find(int value) {
        while (parent[value] != value) {
            parent[value] = parent[parent[value]];
            value = parent[value];
        }
        return value;
    }
    void join(int left, int right) {
        left = find(left);
        right = find(right);
        if (left != right) parent[right] = left;
    }
};

struct Shape {
    std::vector<Edge> sorted_edges;
    // parent component, child component, index in sorted_edges
    std::vector<std::array<int, 3>> directed;
};

static std::vector<Shape> make_shapes(int count) {
    std::vector<Shape> result;
    std::uint64_t code_count = 1;
    for (int index = 0; index < count - 2; ++index) code_count *= count;
    for (std::uint64_t packed = 0; packed < code_count; ++packed) {
        auto value = packed;
        std::vector<int> code(count - 2);
        std::vector<int> degree(count, 1);
        for (int& item : code) {
            item = int(value % count);
            value /= count;
            ++degree[item];
        }
        std::vector<Edge> edges;
        for (int item : code) {
            int leaf = 0;
            while (degree[leaf] != 1) ++leaf;
            edges.emplace_back(std::min(leaf, item), std::max(leaf, item));
            --degree[leaf];
            --degree[item];
        }
        int first = -1;
        int second = -1;
        for (int index = 0; index < count; ++index) {
            if (degree[index] == 1) {
                if (first < 0) first = index;
                else second = index;
            }
        }
        edges.emplace_back(std::min(first, second), std::max(first, second));
        std::sort(edges.begin(), edges.end());

        std::vector<std::vector<std::pair<int, int>>> adjacency(count);
        for (int index = 0; index < int(edges.size()); ++index) {
            const auto [left, right] = edges[index];
            adjacency[left].emplace_back(right, index);
            adjacency[right].emplace_back(left, index);
        }
        std::vector<bool> seen(count);
        std::queue<int> queue;
        queue.push(0);
        seen[0] = true;
        std::vector<std::array<int, 3>> directed;
        while (!queue.empty()) {
            const int parent = queue.front();
            queue.pop();
            std::sort(adjacency[parent].begin(), adjacency[parent].end());
            for (const auto [child, edge_index] : adjacency[parent]) {
                if (seen[child]) continue;
                seen[child] = true;
                queue.push(child);
                directed.push_back({parent, child, edge_index});
            }
        }
        if (int(directed.size()) != count - 1) std::abort();
        result.push_back({std::move(edges), std::move(directed)});
    }
    std::sort(result.begin(), result.end(), [](const Shape& left, const Shape& right) {
        return left.sorted_edges < right.sorted_edges;
    });
    const auto duplicate = std::adjacent_find(
        result.begin(), result.end(), [](const Shape& left, const Shape& right) {
            return left.sorted_edges == right.sorted_edges;
        });
    if (duplicate != result.end()) std::abort();
    return result;
}

static std::size_t working_set_bytes() {
#ifdef _WIN32
    PROCESS_MEMORY_COUNTERS counters{};
    counters.cb = sizeof(counters);
    if (GetProcessMemoryInfo(GetCurrentProcess(), &counters, sizeof(counters))) {
        return counters.WorkingSetSize;
    }
#endif
    return 0;
}

struct Search {
    int radius = 4;
    double timeout_seconds = 300.0;
    std::chrono::steady_clock::time_point started;
    Matrix A = transition_matrix();
    State origin;
    std::array<Edge, N> old_edges{};
    std::array<std::uint32_t, N + 1> old_state{};
    std::vector<int> heavy;
    std::vector<Shape> shapes;
    std::vector<std::vector<int>> components;
    std::array<int, N + 1> component_of{};
    std::vector<std::uint32_t> delta;
    std::vector<bool> assigned;
    std::array<Edge, N> chosen_edges{};
    std::uint32_t unassigned_labels = 0;
    bool timed_out = false;
    bool found = false;
    bool enforce_b = true;
    State answer;
    std::vector<int> answer_removed;

    std::uint64_t eligible_sets = 0;
    std::uint64_t visited_sets = 0;
    std::uint64_t root_prunes = 0;
    std::uint64_t searched_sets = 0;
    std::uint64_t shape_assignments = 0;
    std::uint64_t endpoint_branches = 0;
    std::uint64_t partial_prunes = 0;
    std::uint64_t valid_leaves = 0;
    std::size_t peak_working_set = 0;

    bool expired() {
        peak_working_set = std::max(peak_working_set, working_set_bytes());
        const auto elapsed = std::chrono::duration<double>(
            std::chrono::steady_clock::now() - started).count();
        timed_out = elapsed >= timeout_seconds;
        return timed_out;
    }

    bool partial_valid() {
        for (int component = 0; component < int(components.size()); ++component) {
            if (!assigned[component]) continue;
            for (int vertex : components[component]) {
                if (vertex == GROUND) continue;
                const std::uint32_t t = old_state[vertex] ^ delta[component];
                if (std::popcount(t) > 4) {
                    ++partial_prunes;
                    return false;
                }
                if (!enforce_b) continue;
                if (t & unassigned_labels) continue;
                std::uint32_t b = 0;
                auto remaining = t;
                while (remaining) {
                    const int label = std::countr_zero(remaining);
                    b ^= row_from_edge(chosen_edges[label]);
                    remaining &= remaining - 1;
                }
                const int b_weight = std::popcount(b);
                if (b_weight > 4 || std::popcount(t) > b_weight) {
                    ++partial_prunes;
                    return false;
                }
            }
        }
        return true;
    }

    void dfs(const Shape& shape, const std::vector<int>& labels, int depth) {
        if (found || timed_out) return;
        if (depth == radius) {
            ++valid_leaves;
            Matrix C{};
            for (int label = 0; label < N; ++label) C[label] = row_from_edge(chosen_edges[label]);
            State state;
            if (!from_C(C, state)) std::abort();
            for (int row = 0; row < N; ++row) {
                if (std::popcount(state.T[row]) > 4
                    || (enforce_b && (std::popcount(state.B[row]) > 4
                        || std::popcount(state.T[row]) > std::popcount(state.B[row])))) {
                    std::abort();
                }
            }
            if (multiply(state.C, state.T) != A || multiply(state.T, state.C) != state.B) {
                std::abort();
            }
            answer = state;
            found = true;
            return;
        }
        const auto [parent, child, edge_index] = shape.directed[depth];
        const int label = labels[edge_index];
        if (!assigned[parent] || assigned[child]) std::abort();
        const auto old_unassigned = unassigned_labels;
        unassigned_labels &= ~(std::uint32_t{1} << label);
        assigned[child] = true;
        for (int left : components[parent]) {
            for (int right : components[child]) {
                const std::uint32_t child_delta = delta[parent] ^ old_state[left]
                    ^ old_state[right] ^ A[label];
                bool low = true;
                for (int vertex : components[child]) {
                    if (vertex != GROUND
                        && std::popcount(old_state[vertex] ^ child_delta) > 4) {
                        low = false;
                        break;
                    }
                }
                if (!low) continue;
                ++endpoint_branches;
                if ((endpoint_branches & 0xffffU) == 0 && expired()) break;
                delta[child] = child_delta;
                chosen_edges[label] = {left, right};
                if (partial_valid()) dfs(shape, labels, depth + 1);
                if (found || timed_out) break;
            }
            if (found || timed_out) break;
        }
        assigned[child] = false;
        unassigned_labels = old_unassigned;
    }

    void search_removed(const std::vector<int>& removed) {
        ++visited_sets;
        Dsu dsu;
        std::array<bool, N> is_removed{};
        for (int label : removed) is_removed[label] = true;
        for (int label = 0; label < N; ++label) {
            if (!is_removed[label]) dsu.join(old_edges[label].first, old_edges[label].second);
        }
        std::vector<std::vector<int>> raw;
        std::array<int, N + 1> root_to_index{};
        root_to_index.fill(-1);
        for (int vertex = 0; vertex <= N; ++vertex) {
            const int root = dsu.find(vertex);
            if (root_to_index[root] < 0) {
                root_to_index[root] = int(raw.size());
                raw.push_back({});
            }
            raw[root_to_index[root]].push_back(vertex);
        }
        if (int(raw.size()) != radius + 1) std::abort();
        int root_index = 0;
        while (std::find(raw[root_index].begin(), raw[root_index].end(), GROUND)
               == raw[root_index].end()) ++root_index;
        std::swap(raw[0], raw[root_index]);
        std::sort(raw.begin() + 1, raw.end());
        components = std::move(raw);
        for (int index = 0; index < int(components.size()); ++index) {
            for (int vertex : components[index]) component_of[vertex] = index;
        }
        for (int vertex : heavy) {
            if (component_of[vertex] == 0) {
                ++root_prunes;
                return;
            }
        }
        ++searched_sets;
        for (int label = 0; label < N; ++label) chosen_edges[label] = old_edges[label];
        unassigned_labels = 0;
        for (int label : removed) unassigned_labels |= std::uint32_t{1} << label;
        delta.assign(radius + 1, 0);
        assigned.assign(radius + 1, false);
        assigned[0] = true;
        if (!partial_valid()) return;

        for (const auto& shape : shapes) {
            auto labels = removed;
            std::sort(labels.begin(), labels.end());
            do {
                ++shape_assignments;
                dfs(shape, labels, 0);
                if (found || ((shape_assignments & 0xffffU) == 0 && expired())) return;
            } while (std::next_permutation(labels.begin(), labels.end()));
        }
    }

    void enumerate_removed(int next, std::vector<int>& selected) {
        if (found || timed_out) return;
        if (int(selected.size()) == radius) {
            const bool forced = std::find(selected.begin(), selected.end(), 16) != selected.end()
                && (std::find(selected.begin(), selected.end(), 12) != selected.end()
                    || std::find(selected.begin(), selected.end(), 29) != selected.end());
            if (!forced) return;
            ++eligible_sets;
            search_removed(selected);
            if ((searched_sets % 100) == 0 && searched_sets) {
                std::fprintf(stderr,
                    "searched=%llu assignments=%llu branches=%llu leaves=%llu\n",
                    static_cast<unsigned long long>(searched_sets),
                    static_cast<unsigned long long>(shape_assignments),
                    static_cast<unsigned long long>(endpoint_branches),
                    static_cast<unsigned long long>(valid_leaves));
            }
            return;
        }
        const int needed = radius - int(selected.size());
        for (int value = next; value <= N - needed; ++value) {
            selected.push_back(value);
            enumerate_removed(value + 1, selected);
            selected.pop_back();
            if (found || timed_out) return;
        }
    }
};

static void write_report(const char* path, Search& search, const char* start_path) {
    const auto elapsed = std::chrono::duration<double>(
        std::chrono::steady_clock::now() - search.started).count();
    search.peak_working_set = std::max(search.peak_working_set, working_set_bytes());
    std::string json_start(start_path);
    std::replace(json_start.begin(), json_start.end(), '\\', '/');
    std::ofstream out(path);
    out << "{\n"
        << "  \"schema\": 1,\n"
        << "  \"status\": \"" << (search.found ? "sat" : search.timed_out ? "unknown" : "unsat") << "\",\n"
        << "  \"reason_unknown\": " << (search.timed_out ? "\"timeout\"" : "null") << ",\n"
        << "  \"scope\": \"exact C-row Hamming radius <=" << search.radius
        << (search.enforce_b
            ? "; shallow C, T/B<=4, tick-zero capacity\",\n"
            : "; shallow C, T<=4 only (B relaxed)\",\n")
        << "  \"start\": \"" << json_start << "\",\n"
        << "  \"radius\": " << search.radius << ",\n"
        << "  \"component_tree_shape_count\": " << search.shapes.size() << ",\n"
        << "  \"eligible_removed_set_count\": " << search.eligible_sets << ",\n"
        << "  \"visited_removed_sets\": " << search.visited_sets << ",\n"
        << "  \"root_component_prunes\": " << search.root_prunes << ",\n"
        << "  \"searched_removed_sets\": " << search.searched_sets << ",\n"
        << "  \"shape_label_assignments\": " << search.shape_assignments << ",\n"
        << "  \"endpoint_offset_branches\": " << search.endpoint_branches << ",\n"
        << "  \"partial_prunes\": " << search.partial_prunes << ",\n"
        << "  \"valid_leaves\": " << search.valid_leaves << ",\n"
        << "  \"timeout_seconds\": " << search.timeout_seconds << ",\n"
        << "  \"peak_working_set_mb\": " << (double(search.peak_working_set) / 1048576.0) << ",\n"
        << "  \"elapsed_seconds\": " << elapsed;
    if (search.found) {
        out << ",\n  \"certificate\": {\n";
        for (const auto [name, matrix] : std::array<std::pair<const char*, const Matrix*>, 3>{
                 std::pair{"C", &search.answer.C}, {"T", &search.answer.T}, {"B", &search.answer.B}}) {
            out << "    \"" << name << "\": [";
            char value[16];
            for (int row = 0; row < N; ++row) {
                std::snprintf(value, sizeof(value), "\"%08x\"", (*matrix)[row]);
                out << (row ? "," : "") << value;
            }
            out << "]" << (name[0] == 'B' ? "\n" : ",\n");
        }
        out << "  }\n";
    } else {
        out << "\n";
    }
    out << "}\n";
}

int main(int argc, char** argv) {
    if (argc < 5) {
        std::fprintf(stderr, "usage: search_radius START OUTPUT RADIUS TIMEOUT_SECONDS [t-only]\n");
        return 64;
    }
    Search search;
    search.radius = std::atoi(argv[3]);
    search.timeout_seconds = std::atof(argv[4]);
    search.enforce_b = !(argc >= 6 && std::string(argv[5]) == "t-only");
    if (search.radius < 4 || search.radius > 6) {
        std::fprintf(stderr, "radius must be 4..6\n");
        return 64;
    }
    Matrix C;
    if (!load_C(argv[1], C) || !from_C(C, search.origin)) {
        std::fprintf(stderr, "failed to load start\n");
        return 65;
    }
    for (int label = 0; label < N; ++label) search.old_edges[label] = edge_from_row(C[label]);
    for (int vertex = 0; vertex < N; ++vertex) {
        search.old_state[vertex] = search.origin.T[vertex];
        if (std::popcount(search.origin.T[vertex]) > 4) search.heavy.push_back(vertex);
    }
    search.old_state[GROUND] = 0;
    search.shapes = make_shapes(search.radius + 1);
    search.started = std::chrono::steady_clock::now();
    std::vector<int> removed;
    search.enumerate_removed(0, removed);
    write_report(argv[2], search, argv[1]);
    std::printf("status=%s radius=%d eligible=%llu visited=%llu searched=%llu "
                "assignments=%llu branches=%llu leaves=%llu peak_mb=%.2f\n",
        search.found ? "sat" : search.timed_out ? "unknown" : "unsat",
        search.radius,
        static_cast<unsigned long long>(search.eligible_sets),
        static_cast<unsigned long long>(search.visited_sets),
        static_cast<unsigned long long>(search.searched_sets),
        static_cast<unsigned long long>(search.shape_assignments),
        static_cast<unsigned long long>(search.endpoint_branches),
        static_cast<unsigned long long>(search.valid_leaves),
        double(search.peak_working_set) / 1048576.0);
    return search.found || !search.timed_out ? 0 : 2;
}
