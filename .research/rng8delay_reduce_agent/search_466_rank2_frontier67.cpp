#define RNG_CALIBRATED_LIBRARY
#include "search_calibrated_global_67.cpp"

#include <chrono>
#include <cmath>
#include <map>
#include <unordered_map>

namespace {

using RankKey = std::tuple<long long, int, int, int, int, std::uint64_t>;

struct Candidate {
    State state{};
    StructuralScore structural{};
    Bound bound{};
    long long calibrated = 0;
    int depth = 0;
    int first_destination = -1;
    int first_source = -1;
    int second_destination = -1;
    int second_source = -1;
    std::uint64_t hash = 0;
};

class TopSet {
public:
    enum class Mode { Strict, Proxy, Calibrated, Xor };

    TopSet(Mode mode, std::size_t capacity) : mode_(mode), capacity_(capacity) {}

    void insert(const Candidate& candidate) {
        const auto key = rank_key(candidate);
        entries_[key] = candidate;
        if (entries_.size() > capacity_) entries_.erase(std::prev(entries_.end()));
    }

    const std::map<RankKey, Candidate>& entries() const { return entries_; }

private:
    RankKey rank_key(const Candidate& candidate) const {
        const auto& bound = candidate.bound;
        const int total_weight = candidate.structural.total_weight;
        switch (mode_) {
            case Mode::Strict:
                return {bound.strict_logic, bound.proxy_logic, bound.greedy_xor,
                        static_cast<int>(candidate.calibrated / 1000), total_weight,
                        candidate.hash};
            case Mode::Proxy:
                return {bound.proxy_logic, bound.strict_logic, bound.greedy_xor,
                        static_cast<int>(candidate.calibrated / 1000), total_weight,
                        candidate.hash};
            case Mode::Calibrated:
                return {candidate.calibrated, bound.strict_logic, bound.proxy_logic,
                        bound.greedy_xor, total_weight, candidate.hash};
            case Mode::Xor:
                return {bound.greedy_xor, bound.strict_logic, bound.proxy_logic,
                        static_cast<int>(candidate.calibrated / 1000), total_weight,
                        candidate.hash};
        }
        throw std::runtime_error("unknown top-set mode");
    }

    Mode mode_;
    std::size_t capacity_;
    std::map<RankKey, Candidate> entries_;
};

State read_first(const std::string& path) {
    std::ifstream input(path);
    if (!input) throw std::runtime_error("cannot open center JSONL");
    std::string line;
    while (std::getline(input, line)) {
        if (line.empty()) continue;
        State state{};
        if (!parse_matrix(line, "T", state.T)
            || !parse_matrix(line, "B", state.B)
            || !parse_matrix(line, "C", state.C)) {
            throw std::runtime_error("center parse failure");
        }
        return state;
    }
    throw std::runtime_error("center JSONL is empty");
}

bool phase67_feasible(const State& state) {
    for (int row = 0; row < kBits; ++row) {
        const int steady_weight = std::popcount(state.B[row]);
        const int target_weight = std::popcount(state.T[row]);
        // One direct mode leaf carries one seed bit; a weight-three final has
        // one pair label (<=2) plus one direct label (<=1).
        if ((steady_weight == 1 || steady_weight == 3) && target_weight > 3) {
            return false;
        }
    }
    return true;
}

long long raw_calibrated(const Bound& b) {
    const double strict = b.strict_logic;
    const double proxy = b.proxy_logic;
    const double heavy = b.heavy_finals;
    const double forced = b.forced_low_finals;
    const double pair = b.pair_node_lower;
    const double dual = b.dual_pair_lower;
    const double mode = b.mode_or_lower;
    const double direct_not = b.direct_not_lower;
    const double greedy = b.greedy_xor;
    const double value =
        -38.37381425013302
        + 0.2907130540493803 * strict
        + 1.446975548831352 * proxy
        - 0.7974479435392698 * heavy
        + 1.013165381312974 * forced
        + 0.06141426318165477 * pair
        + 0.06141426302057562 * dual
        + 1.1350581911141866 * mode
        - 1.9528818859109456 * direct_not
        - 1.3637959212621382 * greedy
        - 0.4869901758929597 * heavy * forced
        + 0.21049739406004694 * forced * pair
        + 0.02472894185977398 * heavy * mode
        - 0.11926640371493188 * pair * mode
        + 0.05905225954766324 * (greedy - 61.0) * (greedy - 61.0);
    return static_cast<long long>(std::llround(value * 1'000'000.0));
}

void emit_candidate(std::ostream& output, const Candidate& candidate) {
    const auto& b = candidate.bound;
    output << "{\"center\":\"best294\",\"depth\":" << candidate.depth;
    if (candidate.depth >= 1) {
        output << ",\"move1\":[" << candidate.first_destination << ','
               << candidate.first_source << ']';
    }
    if (candidate.depth >= 2) {
        output << ",\"move2\":[" << candidate.second_destination << ','
               << candidate.second_source << ']';
    }
    output << ",\"hash\":\"" << std::hex << std::setw(16)
           << std::setfill('0') << candidate.hash << std::dec << std::setfill(' ')
           << "\",\"lower\":{\"strict_logic\":" << b.strict_logic
           << ",\"proxy_logic\":" << b.proxy_logic
           << ",\"greedy_xor\":" << b.greedy_xor
           << ",\"heavy_finals\":" << b.heavy_finals
           << ",\"forced_low_finals\":" << b.forced_low_finals
           << ",\"pair_node_lower\":" << b.pair_node_lower
           << ",\"dual_pair_lower\":" << b.dual_pair_lower
           << ",\"mode_or_lower\":" << b.mode_or_lower
           << ",\"direct_not_lower\":" << b.direct_not_lower
           << ",\"calibrated_micro\":" << candidate.calibrated << "},";
    emit_matrix(output, "T", candidate.state.T);
    output << ',';
    emit_matrix(output, "B", candidate.state.B);
    output << ',';
    emit_matrix(output, "C", candidate.state.C);
    output << "}\n";
}

}  // namespace

int main(int argc, char** argv) {
    std::string center_path;
    std::string output_path;
    std::string summary_path;
    std::size_t capacity = 128;
    for (int index = 1; index < argc; ++index) {
        const std::string argument = argv[index];
        auto next = [&]() -> std::string {
            if (++index >= argc) throw std::runtime_error("missing argument value");
            return argv[index];
        };
        if (argument == "--center") center_path = next();
        else if (argument == "--output") output_path = next();
        else if (argument == "--summary") summary_path = next();
        else if (argument == "--capacity") capacity = std::stoull(next());
        else throw std::runtime_error("unknown argument: " + argument);
    }
    if (center_path.empty() || output_path.empty() || summary_path.empty()) {
        throw std::runtime_error("--center, --output and --summary are required");
    }

    const auto started = std::chrono::steady_clock::now();
    const auto A = matrix_from_xorshift();
    const State center = read_first(center_path);
    if (multiply(center.C, center.T) != A || multiply(center.T, center.C) != center.B) {
        throw std::runtime_error("center algebra identity failure");
    }

    TopSet strict(TopSet::Mode::Strict, capacity);
    TopSet proxy(TopSet::Mode::Proxy, capacity);
    TopSet calibrated(TopSet::Mode::Calibrated, capacity);
    TopSet xors(TopSet::Mode::Xor, capacity);
    std::uint64_t tested = 0;
    std::uint64_t structurally_feasible = 0;
    std::uint64_t phase_feasible = 0;

    auto test = [&](const State& state, int depth, int d1, int s1, int d2, int s2) {
        ++tested;
        const auto structural = structural_score(state);
        if (!structural.feasible()) return;
        ++structurally_feasible;
        if (!phase67_feasible(state)) return;
        const auto bound = lower_bound(state);
        if (bound.strict_logic >= 1000 || bound.proxy_logic >= 1000
            || bound.greedy_xor >= 1000) return;
        ++phase_feasible;
        Candidate candidate{
            state, structural, bound, raw_calibrated(bound), depth,
            d1, s1, d2, s2, state_hash(state.T)
        };
        strict.insert(candidate);
        proxy.insert(candidate);
        calibrated.insert(candidate);
        xors.insert(candidate);
    };

    std::vector<std::pair<int, int>> moves;
    for (int destination = 0; destination < kBits; ++destination) {
        for (int source = 0; source < kBits; ++source) {
            if (source != destination) moves.push_back({destination, source});
        }
    }

    test(center, 0, -1, -1, -1, -1);
    for (const auto [destination, source] : moves) {
        State state = center;
        mutate(state, destination, source);
        test(state, 1, destination, source, -1, -1);
    }
    for (const auto [first_destination, first_source] : moves) {
        State first = center;
        mutate(first, first_destination, first_source);
        for (const auto [second_destination, second_source] : moves) {
            State state = first;
            mutate(state, second_destination, second_source);
            test(state, 2, first_destination, first_source,
                 second_destination, second_source);
        }
    }

    std::ofstream output(output_path, std::ios::trunc);
    if (!output) throw std::runtime_error("cannot create frontier JSONL");
    std::unordered_map<std::uint64_t, bool> emitted;
    std::size_t output_count = 0;
    const std::array<const TopSet*, 4> fronts{&strict, &proxy, &calibrated, &xors};
    for (std::size_t rank = 0; rank < capacity; ++rank) {
        for (const auto* front : fronts) {
            if (rank >= front->entries().size()) continue;
            auto iterator = front->entries().begin();
            std::advance(iterator, static_cast<std::ptrdiff_t>(rank));
            const auto& candidate = iterator->second;
            if (!emitted.emplace(candidate.hash, true).second) continue;
            emit_candidate(output, candidate);
            ++output_count;
        }
    }

    const double elapsed = std::chrono::duration<double>(
        std::chrono::steady_clock::now() - started
    ).count();
    const auto& best_strict = strict.entries().begin()->second;
    const auto& best_proxy = proxy.entries().begin()->second;
    const auto& best_calibrated = calibrated.entries().begin()->second;
    const auto& best_xor = xors.entries().begin()->second;
    std::ofstream summary(summary_path, std::ios::trunc);
    if (!summary) throw std::runtime_error("cannot create summary JSON");
    summary << "{\n  \"schema\": 1,\n"
            << "  \"scope\": \"complete 67-cycle elementary basis-move sequence length <=2 around best294\",\n"
            << "  \"center\": " << std::quoted(center_path) << ",\n"
            << "  \"tested\": " << tested << ",\n"
            << "  \"structurally_feasible\": " << structurally_feasible << ",\n"
            << "  \"phase67_feasible\": " << phase_feasible << ",\n"
            << "  \"front_capacity\": " << capacity << ",\n"
            << "  \"emitted_unique\": " << output_count << ",\n"
            << "  \"elapsed_seconds\": " << std::fixed << std::setprecision(6)
            << elapsed << ",\n"
            << "  \"best\": {\n"
            << "    \"strict_logic\": " << best_strict.bound.strict_logic << ",\n"
            << "    \"proxy_logic\": " << best_proxy.bound.proxy_logic << ",\n"
            << "    \"calibrated_micro\": " << best_calibrated.calibrated << ",\n"
            << "    \"greedy_xor\": " << best_xor.bound.greedy_xor << "\n"
            << "  }\n}\n";
    std::fprintf(stderr,
        "tested=%llu structural=%llu phase67=%llu emitted=%zu "
        "best_strict=%d best_proxy=%d best_xor=%d elapsed=%.3f\n",
        static_cast<unsigned long long>(tested),
        static_cast<unsigned long long>(structurally_feasible),
        static_cast<unsigned long long>(phase_feasible), output_count,
        best_strict.bound.strict_logic, best_proxy.bound.proxy_logic,
        best_xor.bound.greedy_xor, elapsed);
    return 0;
}
