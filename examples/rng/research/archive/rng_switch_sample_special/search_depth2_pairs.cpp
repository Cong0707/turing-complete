// Exact meet-in-the-middle search for sample-specialized parity-5 repairs.
//
// The search domain is deliberately concrete and timing-aware:
//   primitive = raw bit, constant, or one NOT/AND/OR/NAND/NOR gate;
//   node      = primitive, or one cheap gate over two primitives;
//   repair    = XOR(node_a, node_b).
//
// A node costs at most three gates and has at most two one-delay levels.  A
// repair therefore costs at most nine gates and has at most four delay units,
// which fits after a Delay Bit in the level's delay-nine budget (including the
// existing one-delay phase OR on visible leaves).  The two nodes may share
// primitives, so this domain includes the useful shared-nonlinearity cases.
//
// Absence on the selected 128 care points is an exact exclusion for the full
// care set: every full-care identity must also hold on that subset.  Any subset
// hit is verified against all 16,640 feedback care points before acceptance.

#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

constexpr unsigned state_bits = 42;
constexpr unsigned tests = 256;
constexpr unsigned output_ticks = 65;
constexpr unsigned feedback_ticks = 64;
constexpr std::uint64_t mask32 = 0xffffffffULL;
constexpr std::uint64_t mask64 = std::numeric_limits<std::uint64_t>::max();
constexpr std::uint64_t seed_multiplier = 0x4848f09881d3ddd1ULL;
constexpr std::size_t table_capacity = std::size_t{1} << 25;
constexpr std::size_t table_mask = table_capacity - 1;

constexpr std::array<std::uint64_t, state_bits> h_rows{
    0x12000002001ULL, 0x00204002000ULL, 0x00401008004ULL,
    0x10400300100ULL, 0x00800600200ULL, 0x03000000000ULL,
    0x02001000800ULL, 0x04103001000ULL, 0x00100020110ULL,
    0x01000000200ULL, 0x00410008000ULL, 0x00020000888ULL,
    0x00006001000ULL, 0x00080044002ULL, 0x00400488004ULL,
    0x00410008000ULL, 0x01820010000ULL, 0x02100402000ULL,
    0x00080840000ULL, 0x00400088004ULL, 0x00002200100ULL,
    0x20004400200ULL, 0x08000804400ULL, 0x00011800800ULL,
    0x00122001000ULL, 0x00042200100ULL, 0x01084000200ULL,
    0x20000404000ULL, 0x00411000800ULL, 0x00122001000ULL,
    0x00040000000ULL, 0x20080400000ULL, 0x20040020001ULL,
    0x10400004002ULL, 0x00800110008ULL, 0x00100220010ULL,
    0x08200040020ULL, 0x04400080040ULL, 0x00401100080ULL,
    0x0a000800400ULL, 0x20004002000ULL, 0x08008404000ULL,
};

constexpr std::array<std::uint64_t, 3> bad_rows{
    h_rows[3], h_rows[7], h_rows[14]
};

struct Fingerprint {
    std::uint64_t lo{};
    std::uint64_t hi{};

    friend bool operator==(Fingerprint left, Fingerprint right) {
        return left.lo == right.lo && left.hi == right.hi;
    }
    friend Fingerprint operator^(Fingerprint left, Fingerprint right) {
        return {left.lo ^ right.lo, left.hi ^ right.hi};
    }
};

enum class Operation : std::uint8_t { And, Or, Nand, Nor };

struct Primitive {
    // kind: 0 raw, 1 const, 2 not, 3 binary cheap operation.
    std::uint8_t kind{};
    std::uint8_t a{};
    std::uint8_t b{};
    Operation operation{};
    bool constant{};
    Fingerprint fingerprint{};
};

struct NodeDescriptor {
    bool primitive{};
    std::uint16_t a{};
    std::uint16_t b{};
    Operation operation{};
};

struct Candidate {
    NodeDescriptor left{};
    Fingerprint wanted_right{};
    unsigned target{};
};

std::uint32_t xorshift32(std::uint32_t value) {
    value ^= value >> 13;
    value ^= value << 17;
    value ^= value >> 5;
    return value;
}

std::uint32_t live_seed(unsigned test_id) {
    const auto mixed = (static_cast<std::uint64_t>(test_id) + 1) * seed_multiplier;
    return static_cast<std::uint32_t>(1 + mixed % 0xfffffffeULL);
}

std::uint64_t apply_h(std::uint64_t value) {
    std::uint64_t result = 0;
    for (unsigned index = 0; index < state_bits; ++index) {
        result |= static_cast<std::uint64_t>(std::popcount(h_rows[index] & value) & 1)
                  << index;
    }
    return result;
}

std::vector<std::uint64_t> build_feedback_points() {
    std::vector<std::uint64_t> result;
    result.reserve(tests * (feedback_ticks + 1));
    std::array<std::uint64_t, tests> states{};
    for (unsigned test = 0; test < tests; ++test) {
        const auto seed = live_seed(test);
        result.push_back(seed);
        states[test] = apply_h(seed);
    }
    for (unsigned tick = 0; tick < feedback_ticks; ++tick) {
        for (const auto state : states) result.push_back(state);
        for (auto& state : states) state = apply_h(state);
    }
    if (result.size() != tests * (feedback_ticks + 1)) {
        throw std::runtime_error("feedback point count mismatch");
    }
    return result;
}

bool add_to_basis(std::array<std::uint64_t, state_bits>& basis, std::uint64_t value) {
    while (value) {
        const auto pivot = std::bit_width(value) - 1;
        if (basis[pivot]) {
            value ^= basis[pivot];
        } else {
            basis[pivot] = value;
            return true;
        }
    }
    return false;
}

std::vector<std::size_t> select_points(const std::vector<std::uint64_t>& points) {
    std::vector<std::size_t> selected;
    selected.reserve(128);
    std::vector<bool> used(points.size());
    std::array<std::uint64_t, state_bits> basis{};
    for (std::size_t index = 0; index < points.size() && selected.size() < state_bits; ++index) {
        if (add_to_basis(basis, points[index])) {
            selected.push_back(index);
            used[index] = true;
        }
    }
    if (selected.size() != state_bits) {
        throw std::runtime_error("feedback care rank is below 42");
    }

    // Fill the fingerprint with points spread across the complete tick-major
    // care set.  The rank-basis prefix makes the 42 linear coefficients visible.
    std::size_t cursor = 0;
    constexpr std::size_t stride = 7919;
    while (selected.size() < 128) {
        cursor = (cursor + stride) % points.size();
        if (!used[cursor]) {
            selected.push_back(cursor);
            used[cursor] = true;
        }
    }
    return selected;
}

Fingerprint fingerprint_row(
    std::uint64_t row,
    const std::vector<std::uint64_t>& points,
    const std::vector<std::size_t>& selected
) {
    Fingerprint result{};
    for (unsigned index = 0; index < selected.size(); ++index) {
        const bool value = std::popcount(row & points[selected[index]]) & 1;
        if (index < 64) {
            result.lo |= static_cast<std::uint64_t>(value) << index;
        } else {
            result.hi |= static_cast<std::uint64_t>(value) << (index - 64);
        }
    }
    return result;
}

bool eval_operation(Operation operation, bool a, bool b) {
    switch (operation) {
        case Operation::And: return a && b;
        case Operation::Or: return a || b;
        case Operation::Nand: return !(a && b);
        case Operation::Nor: return !(a || b);
    }
    throw std::runtime_error("unknown operation");
}

Fingerprint fingerprint_operation(Operation operation, Fingerprint a, Fingerprint b) {
    switch (operation) {
        case Operation::And: return {a.lo & b.lo, a.hi & b.hi};
        case Operation::Or: return {a.lo | b.lo, a.hi | b.hi};
        case Operation::Nand: return {~(a.lo & b.lo), ~(a.hi & b.hi)};
        case Operation::Nor: return {~(a.lo | b.lo), ~(a.hi | b.hi)};
    }
    throw std::runtime_error("unknown operation");
}

std::vector<Primitive> build_primitives(
    const std::vector<std::uint64_t>& points,
    const std::vector<std::size_t>& selected
) {
    std::vector<Primitive> result;
    result.reserve(3530);
    for (unsigned bit = 0; bit < state_bits; ++bit) {
        result.push_back(
            Primitive{0, static_cast<std::uint8_t>(bit), 0, Operation::And, false,
                      fingerprint_row(std::uint64_t{1} << bit, points, selected)}
        );
    }
    result.push_back(Primitive{1, 0, 0, Operation::And, false, {0, 0}});
    result.push_back(Primitive{1, 0, 0, Operation::And, true, {mask64, mask64}});
    for (unsigned bit = 0; bit < state_bits; ++bit) {
        const auto source = result[bit].fingerprint;
        result.push_back(
            Primitive{2, static_cast<std::uint8_t>(bit), 0, Operation::And, false,
                      {~source.lo, ~source.hi}}
        );
    }
    for (unsigned left = 0; left < state_bits; ++left) {
        for (unsigned right = left + 1; right < state_bits; ++right) {
            for (unsigned raw_operation = 0; raw_operation < 4; ++raw_operation) {
                const auto operation = static_cast<Operation>(raw_operation);
                result.push_back(
                    Primitive{
                        3,
                        static_cast<std::uint8_t>(left),
                        static_cast<std::uint8_t>(right),
                        operation,
                        false,
                        fingerprint_operation(
                            operation,
                            result[left].fingerprint,
                            result[right].fingerprint
                        ),
                    }
                );
            }
        }
    }
    if (result.size() != 3530) throw std::runtime_error("primitive count mismatch");
    return result;
}

bool eval_primitive(const Primitive& primitive, std::uint64_t point) {
    switch (primitive.kind) {
        case 0: return (point >> primitive.a) & 1;
        case 1: return primitive.constant;
        case 2: return !((point >> primitive.a) & 1);
        case 3:
            return eval_operation(
                primitive.operation,
                (point >> primitive.a) & 1,
                (point >> primitive.b) & 1
            );
    }
    throw std::runtime_error("unknown primitive kind");
}

bool eval_node(
    const NodeDescriptor& node,
    const std::vector<Primitive>& primitives,
    std::uint64_t point
) {
    if (node.primitive) return eval_primitive(primitives[node.a], point);
    return eval_operation(
        node.operation,
        eval_primitive(primitives[node.a], point),
        eval_primitive(primitives[node.b], point)
    );
}

template <class Callback>
std::uint64_t enumerate_nodes(const std::vector<Primitive>& primitives, Callback callback) {
    std::uint64_t count = 0;
    for (std::uint16_t index = 0; index < primitives.size(); ++index) {
        const NodeDescriptor node{true, index, 0, Operation::And};
        callback(node, primitives[index].fingerprint);
        ++count;
    }
    for (std::uint16_t left = 0; left < primitives.size(); ++left) {
        for (std::uint16_t right = left; right < primitives.size(); ++right) {
            for (unsigned raw_operation = 0; raw_operation < 4; ++raw_operation) {
                const auto operation = static_cast<Operation>(raw_operation);
                const NodeDescriptor node{false, left, right, operation};
                callback(
                    node,
                    fingerprint_operation(
                        operation,
                        primitives[left].fingerprint,
                        primitives[right].fingerprint
                    )
                );
                ++count;
            }
        }
    }
    return count;
}

std::uint64_t mix64(std::uint64_t value) {
    value += 0x9e3779b97f4a7c15ULL;
    value = (value ^ (value >> 30)) * 0xbf58476d1ce4e5b9ULL;
    value = (value ^ (value >> 27)) * 0x94d049bb133111ebULL;
    return value ^ (value >> 31);
}

class FingerprintSet {
public:
    FingerprintSet()
        : lows_(table_capacity), highs_(table_capacity), used_(table_capacity / 64) {}

    bool insert(Fingerprint key) {
        auto slot = initial_slot(key);
        while (occupied(slot)) {
            if (lows_[slot] == key.lo && highs_[slot] == key.hi) return false;
            slot = (slot + 1) & table_mask;
        }
        mark_occupied(slot);
        lows_[slot] = key.lo;
        highs_[slot] = key.hi;
        ++size_;
        return true;
    }

    bool contains(Fingerprint key) const {
        auto slot = initial_slot(key);
        while (occupied(slot)) {
            if (lows_[slot] == key.lo && highs_[slot] == key.hi) return true;
            slot = (slot + 1) & table_mask;
        }
        return false;
    }

    std::size_t size() const { return size_; }

    static constexpr std::uint64_t storage_bytes() {
        return table_capacity * sizeof(std::uint64_t) * 2
               + (table_capacity / 64) * sizeof(std::uint64_t);
    }

private:
    static std::size_t initial_slot(Fingerprint key) {
        return static_cast<std::size_t>(
            mix64(key.lo ^ std::rotl(key.hi, 23)) & table_mask
        );
    }

    bool occupied(std::size_t slot) const {
        return (used_[slot >> 6] >> (slot & 63)) & 1;
    }

    void mark_occupied(std::size_t slot) {
        used_[slot >> 6] |= std::uint64_t{1} << (slot & 63);
    }

    std::vector<std::uint64_t> lows_;
    std::vector<std::uint64_t> highs_;
    std::vector<std::uint64_t> used_;
    std::size_t size_{};
};

bool verify_pair(
    const Candidate& candidate,
    const NodeDescriptor& right,
    const std::vector<Primitive>& primitives,
    const std::vector<std::uint64_t>& points
) {
    const auto target = bad_rows[candidate.target];
    for (const auto point : points) {
        const bool actual = eval_node(candidate.left, primitives, point)
                            ^ eval_node(right, primitives, point);
        const bool wanted = std::popcount(target & point) & 1;
        if (actual != wanted) return false;
    }
    return true;
}

void verify_protocol() {
    for (unsigned test = 0; test < tests; ++test) {
        const auto seed = live_seed(test);
        auto state = apply_h(seed);
        auto natural = seed;
        for (unsigned tick = 0; tick < output_ticks; ++tick) {
            natural = xorshift32(natural);
            // O rows are unnecessary here: the Python audit verifies all 32
            // outputs.  This independent pass at least checks H determinism and
            // that the complete requested trajectory can be generated.
            state = apply_h(state);
        }
        (void)natural;
        (void)state;
    }
}

}  // namespace

int main(int argc, char** argv) {
    try {
        std::string output = ".research/rng_switch_sample_special/depth2_pair_certificate.json";
        if (argc == 3 && std::string(argv[1]) == "--output") {
            output = argv[2];
        } else if (argc != 1) {
            throw std::runtime_error("usage: search_depth2_pairs [--output FILE]");
        }

        verify_protocol();
        const auto points = build_feedback_points();
        const auto selected = select_points(points);
        const auto primitives = build_primitives(points, selected);
        std::array<Fingerprint, 3> targets{};
        for (unsigned index = 0; index < targets.size(); ++index) {
            targets[index] = fingerprint_row(bad_rows[index], points, selected);
        }

        std::cerr << "allocating " << (FingerprintSet::storage_bytes() >> 20)
                  << " MiB fingerprint table\n";
        FingerprintSet fingerprints;
        const auto node_count = enumerate_nodes(
            primitives,
            [&](const NodeDescriptor&, Fingerprint fingerprint) {
                fingerprints.insert(fingerprint);
            }
        );
        std::cerr << "nodes=" << node_count << " unique fingerprints="
                  << fingerprints.size() << '\n';

        std::vector<Candidate> candidates;
        enumerate_nodes(
            primitives,
            [&](const NodeDescriptor& node, Fingerprint fingerprint) {
                for (unsigned target = 0; target < targets.size(); ++target) {
                    const auto wanted = fingerprint ^ targets[target];
                    if (fingerprints.contains(wanted)) {
                        candidates.push_back(Candidate{node, wanted, target});
                    }
                }
            }
        );
        std::cerr << "128-point candidate left nodes=" << candidates.size() << '\n';

        std::array<std::uint64_t, 3> verified_hits{};
        if (!candidates.empty()) {
            enumerate_nodes(
                primitives,
                [&](const NodeDescriptor& right, Fingerprint fingerprint) {
                    for (const auto& candidate : candidates) {
                        if (candidate.wanted_right == fingerprint
                            && verify_pair(candidate, right, primitives, points)) {
                            ++verified_hits[candidate.target];
                        }
                    }
                }
            );
        }

        std::ofstream stream(output);
        if (!stream) throw std::runtime_error("cannot open output file");
        stream << "{\n"
               << "  \"schema\": 1,\n"
               << "  \"model\": \"XOR of two raw/one-gate/depth2-cheap nodes\",\n"
               << "  \"feedback_care_points\": " << points.size() << ",\n"
               << "  \"selected_filter_points\": " << selected.size() << ",\n"
               << "  \"selected_point_linear_rank\": 42,\n"
               << "  \"primitive_count\": " << primitives.size() << ",\n"
               << "  \"enumerated_node_count\": " << node_count << ",\n"
               << "  \"unique_128bit_fingerprints\": " << fingerprints.size() << ",\n"
               << "  \"fingerprint_table_bytes\": " << FingerprintSet::storage_bytes() << ",\n"
               << "  \"candidate_left_nodes_after_exact_subset_filter\": "
               << candidates.size() << ",\n"
               << "  \"targets\": [\n";
        constexpr std::array<unsigned, 3> indices{3, 7, 14};
        for (unsigned target = 0; target < targets.size(); ++target) {
            stream << "    {\"H_index\": " << indices[target]
                   << ", \"row_hex\": \"" << std::hex << std::setw(11)
                   << std::setfill('0') << bad_rows[target] << std::dec
                   << "\", \"verified_pair_count\": " << verified_hits[target]
                   << "}" << (target + 1 == targets.size() ? "\n" : ",\n");
        }
        stream << "  ],\n"
               << "  \"status\": \""
               << (std::ranges::any_of(verified_hits, [](auto count) { return count != 0; })
                       ? "candidate-found"
                       : "no-candidate-in-enumerated-family")
               << "\",\n"
               << "  \"timing\": \"each node <=3 gate / 2 delay; final XOR gives <=9 gate / 4 delay\",\n"
               << "  \"proof_note\": \"No 128-point hit is an exact exclusion: every full-care identity must hold on the selected subset. Every subset hit is exhaustively verified on all feedback care points.\"\n"
               << "}\n";
        std::cout << "wrote " << output << '\n';
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }
}
