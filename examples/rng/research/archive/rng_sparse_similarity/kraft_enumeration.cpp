// Exact constant-memory Kraft enumeration for the xorshift32 Galois family.
//
// For the Krylov construction in verify_galois_similarity.py, let T0=P^-1
// and B=T0*A*T0^-1.  Every intertwiner producing this same B is
//
//     T = Z*T0,  Z in GF(2)[B].
//
// The characteristic polynomial is primitive, so every nonzero Z is
// invertible.  With D=T*(A+I), one selected weight-two B row of D is a
// bijective 32-bit parameter.  Enumerating every nonzero parameter of weight
// at most eight therefore exhausts every possible solution of
//
//     4*weight(B[i]) + weight(D[i]) <= 16.

#include <array>
#include <bit>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

constexpr int kBits = 32;
constexpr std::uint32_t kPolynomialLow = 0x003ec241U;
constexpr int kParameterRow = 6;

using Matrix = std::array<std::uint32_t, kBits>;

std::uint32_t xorshift32(std::uint32_t value) {
    value ^= value >> 13;
    value ^= value << 17;
    value ^= value >> 5;
    return value;
}

Matrix identity() {
    Matrix result{};
    for (int bit = 0; bit < kBits; ++bit) result[bit] = 1U << bit;
    return result;
}

Matrix matrix_from_xorshift() {
    Matrix result{};
    for (int source = 0; source < kBits; ++source) {
        const auto output = xorshift32(1U << source);
        for (int target = 0; target < kBits; ++target) {
            if ((output >> target) & 1U) result[target] |= 1U << source;
        }
    }
    return result;
}

Matrix rows_from_columns(const Matrix& columns) {
    Matrix result{};
    for (int source = 0; source < kBits; ++source) {
        for (int target = 0; target < kBits; ++target) {
            if ((columns[source] >> target) & 1U) {
                result[target] |= 1U << source;
            }
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

std::uint32_t apply_matrix(const Matrix& matrix, std::uint32_t value) {
    std::uint32_t result = 0;
    for (int row = 0; row < kBits; ++row) {
        if (std::popcount(matrix[row] & value) & 1) result |= 1U << row;
    }
    return result;
}

Matrix multiply(const Matrix& left, const Matrix& right) {
    Matrix result{};
    for (int row = 0; row < kBits; ++row) {
        result[row] = apply_row(left[row], right);
    }
    return result;
}

Matrix add(const Matrix& left, const Matrix& right) {
    Matrix result{};
    for (int row = 0; row < kBits; ++row) result[row] = left[row] ^ right[row];
    return result;
}

Matrix invert(Matrix matrix) {
    Matrix inverse = identity();
    for (int column = 0; column < kBits; ++column) {
        int pivot = column;
        while (pivot < kBits && ((matrix[pivot] >> column) & 1U) == 0) ++pivot;
        if (pivot == kBits) throw std::runtime_error("singular matrix");
        std::swap(matrix[column], matrix[pivot]);
        std::swap(inverse[column], inverse[pivot]);
        for (int row = 0; row < kBits; ++row) {
            if (row != column && ((matrix[row] >> column) & 1U)) {
                matrix[row] ^= matrix[column];
                inverse[row] ^= inverse[column];
            }
        }
    }
    if (matrix != identity()) throw std::runtime_error("inverse reduction failed");
    return inverse;
}

std::uint32_t field_multiply(std::uint32_t left, std::uint32_t right) {
    std::uint32_t result = 0;
    while (right) {
        if (right & 1U) result ^= left;
        right >>= 1;
        const bool carry = (left >> 31) != 0;
        left <<= 1;
        if (carry) left ^= kPolynomialLow;
    }
    return result;
}

std::uint32_t field_power(std::uint32_t base, std::uint64_t exponent) {
    std::uint32_t result = 1;
    while (exponent) {
        if (exponent & 1U) result = field_multiply(result, base);
        base = field_multiply(base, base);
        exponent >>= 1;
    }
    return result;
}

void verify_primitive_polynomial() {
    constexpr std::uint64_t order = 0xffffffffULL;
    constexpr std::array<std::uint64_t, 5> factors = {3, 5, 17, 257, 65537};
    if (field_power(2, 1ULL << 32) != 2 || field_power(2, order) != 1) {
        throw std::runtime_error("polynomial Frobenius/order check failed");
    }
    for (const auto factor : factors) {
        if (field_power(2, order / factor) == 1) {
            throw std::runtime_error("polynomial is not primitive");
        }
    }
}

std::uint64_t binomial(int n, int k) {
    if (k < 0 || k > n) return 0;
    if (k > n - k) k = n - k;
    std::uint64_t result = 1;
    for (int index = 1; index <= k; ++index) {
        result = result * static_cast<std::uint64_t>(n - k + index) /
                 static_cast<std::uint64_t>(index);
    }
    return result;
}

struct Family {
    Matrix a{};
    Matrix p{};
    Matrix t0{};
    Matrix b{};
    Matrix d0{};
    Matrix parameter_from_z{};
    Matrix z_from_parameter{};
    std::array<Matrix, kBits> d_for_parameter_bit{};
    std::array<std::array<std::array<std::uint32_t, 256>, 4>, kBits> lookup{};
};

Family build_family() {
    verify_primitive_polynomial();
    Family family;
    family.a = matrix_from_xorshift();

    Matrix krylov_columns{};
    std::uint32_t value = 1;
    for (int column = 0; column < kBits; ++column) {
        krylov_columns[column] = value;
        value = xorshift32(value);
    }
    family.p = rows_from_columns(krylov_columns);
    family.t0 = invert(family.p);
    family.b = multiply(multiply(family.t0, family.a), family.p);
    family.d0 = multiply(family.t0, add(family.a, identity()));

    Matrix expected_b{};
    expected_b[0] = 0x80000000U;
    for (int row = 1; row < kBits; ++row) expected_b[row] = 1U << (row - 1);
    for (int row = 1; row < kBits; ++row) {
        if ((kPolynomialLow >> row) & 1U) expected_b[row] |= 0x80000000U;
    }
    if (family.b != expected_b) throw std::runtime_error("unexpected companion B");
    if (std::popcount(family.b[kParameterRow]) != 2) {
        throw std::runtime_error("parameter row must be a weight-two B row");
    }

    // The columns of this map are row kParameterRow of B^k*D0.
    Matrix parameter_columns{};
    Matrix b_power = identity();
    std::array<Matrix, kBits> b_powers{};
    for (int exponent = 0; exponent < kBits; ++exponent) {
        b_powers[exponent] = b_power;
        parameter_columns[exponent] =
            multiply(b_power, family.d0)[kParameterRow];
        b_power = multiply(b_power, family.b);
    }
    family.parameter_from_z = rows_from_columns(parameter_columns);
    family.z_from_parameter = invert(family.parameter_from_z);

    // For every unit parameter d=e_bit, recover z and all 32 rows of D.
    for (int bit = 0; bit < kBits; ++bit) {
        const auto z = apply_matrix(family.z_from_parameter, 1U << bit);
        Matrix z_of_b{};
        for (int exponent = 0; exponent < kBits; ++exponent) {
            if ((z >> exponent) & 1U) z_of_b = add(z_of_b, b_powers[exponent]);
        }
        family.d_for_parameter_bit[bit] = multiply(z_of_b, family.d0);
        if (family.d_for_parameter_bit[bit][kParameterRow] != (1U << bit)) {
            throw std::runtime_error("parameter inverse self-check failed");
        }
    }

    for (int row = 0; row < kBits; ++row) {
        for (int chunk = 0; chunk < 4; ++chunk) {
            for (int byte = 0; byte < 256; ++byte) {
                std::uint32_t result = 0;
                for (int bit = 0; bit < 8; ++bit) {
                    if ((byte >> bit) & 1) {
                        result ^= family.d_for_parameter_bit[chunk * 8 + bit][row];
                    }
                }
                family.lookup[row][chunk][byte] = result;
            }
        }
    }
    return family;
}

std::uint32_t transformed_row(const Family& family, int row, std::uint32_t parameter) {
    return family.lookup[row][0][parameter & 0xffU] ^
           family.lookup[row][1][(parameter >> 8) & 0xffU] ^
           family.lookup[row][2][(parameter >> 16) & 0xffU] ^
           family.lookup[row][3][parameter >> 24];
}

std::uint64_t fnv_update(std::uint64_t hash, std::uint32_t value) {
    for (int byte = 0; byte < 4; ++byte) {
        hash ^= (value >> (8 * byte)) & 0xffU;
        hash *= 1099511628211ULL;
    }
    return hash;
}

std::uint64_t family_hash(const Family& family) {
    std::uint64_t hash = 1469598103934665603ULL;
    for (const Matrix* matrix : {&family.a, &family.p, &family.t0, &family.b,
                                 &family.d0, &family.parameter_from_z,
                                 &family.z_from_parameter}) {
        for (const auto row : *matrix) hash = fnv_update(hash, row);
    }
    for (const auto& matrix : family.d_for_parameter_bit) {
        for (const auto row : matrix) hash = fnv_update(hash, row);
    }
    return hash;
}

struct Result {
    bool sat = false;
    std::uint32_t parameter = 0;
    std::uint64_t tested = 0;
    std::array<std::uint64_t, 9> tested_by_weight{};
    std::array<std::uint64_t, kBits> rejected_by_row{};
    std::array<std::array<std::uint64_t, kBits>, 9> rejected_by_weight_row{};
};

Result enumerate(const Family& family) {
    // Check tight rows first.  The selected row is already bounded by the
    // enumeration domain and is omitted from the test order.
    std::vector<int> order;
    for (int row = 0; row < kBits; ++row) {
        if (row != kParameterRow && std::popcount(family.b[row]) == 2) {
            order.push_back(row);
        }
    }
    for (int row = 0; row < kBits; ++row) {
        if (row != kParameterRow && std::popcount(family.b[row]) == 1) {
            order.push_back(row);
        }
    }
    if (order.size() != 31) throw std::runtime_error("bad row test order");

    Result result;
    for (int weight = 1; weight <= 8; ++weight) {
        std::uint64_t parameter = (1ULL << weight) - 1;
        constexpr std::uint64_t limit = 1ULL << 32;
        while (parameter < limit) {
            const auto value = static_cast<std::uint32_t>(parameter);
            ++result.tested;
            ++result.tested_by_weight[weight];
            bool accepted = true;
            for (const int row : order) {
                const int cap = std::popcount(family.b[row]) == 2 ? 8 : 12;
                if (std::popcount(transformed_row(family, row, value)) > cap) {
                    ++result.rejected_by_row[row];
                    ++result.rejected_by_weight_row[weight][row];
                    accepted = false;
                    break;
                }
            }
            if (accepted) {
                result.sat = true;
                result.parameter = value;
                return result;
            }

            const std::uint64_t low = parameter & (~parameter + 1);
            const std::uint64_t ripple = parameter + low;
            parameter = ripple | (((ripple ^ parameter) >> 2) / low);
        }
        if (result.tested_by_weight[weight] != binomial(32, weight)) {
            throw std::runtime_error("combination enumeration count mismatch");
        }
    }
    return result;
}

std::string hex32(std::uint32_t value) {
    std::ostringstream stream;
    stream << std::hex << std::setfill('0') << std::setw(8) << value;
    return stream.str();
}

std::string hex64(std::uint64_t value) {
    std::ostringstream stream;
    stream << std::hex << std::setfill('0') << std::setw(16) << value;
    return stream.str();
}

std::string to_json(const Family& family, const Result& result) {
    std::ostringstream out;
    out << "{\n";
    out << "  \"schema\": 1,\n";
    out << "  \"scope\": \"all nonzero centralizers of fixed xorshift32 Galois B\",\n";
    out << "  \"status\": \"" << (result.sat ? "sat" : "unsat") << "\",\n";
    out << "  \"parameter_row\": " << kParameterRow << ",\n";
    out << "  \"parameter_B_row_hex\": \"" << hex32(family.b[kParameterRow]) << "\",\n";
    out << "  \"parameter_cap\": 8,\n";
    out << "  \"zero_parameter_excluded_as_singular\": true,\n";
    out << "  \"primitive_polynomial_hex\": \"1003ec241\",\n";
    out << "  \"family_fnv1a64\": \"" << hex64(family_hash(family)) << "\",\n";
    out << "  \"tested_nonzero_parameters\": " << result.tested << ",\n";
    out << "  \"complete_domain_size\": 15033172,\n";
    out << "  \"sat_parameter_hex\": "
        << (result.sat ? "\"" + hex32(result.parameter) + "\"" : "null") << ",\n";

    out << "  \"tested_by_weight\": {\n";
    for (int weight = 1; weight <= 8; ++weight) {
        out << "    \"" << weight << "\": " << result.tested_by_weight[weight]
            << (weight == 8 ? "\n" : ",\n");
    }
    out << "  },\n";

    out << "  \"B_rows_hex\": [\n";
    for (int row = 0; row < kBits; ++row) {
        out << "    \"" << hex32(family.b[row]) << "\""
            << (row == kBits - 1 ? "\n" : ",\n");
    }
    out << "  ],\n";

    out << "  \"first_rejection_by_row\": {\n";
    for (int row = 0; row < kBits; ++row) {
        out << "    \"" << row << "\": " << result.rejected_by_row[row]
            << (row == kBits - 1 ? "\n" : ",\n");
    }
    out << "  },\n";

    out << "  \"first_rejection_by_weight_and_row\": {\n";
    for (int weight = 1; weight <= 8; ++weight) {
        out << "    \"" << weight << "\": {";
        for (int row = 0; row < kBits; ++row) {
            if (row) out << ", ";
            out << "\"" << row << "\": "
                << result.rejected_by_weight_row[weight][row];
        }
        out << "}" << (weight == 8 ? "\n" : ",\n");
    }
    out << "  }\n";
    out << "}\n";
    return out.str();
}

}  // namespace

int main(int argc, char** argv) {
    try {
        if (argc > 2) {
            std::cerr << "usage: kraft_enumeration [output.json]\n";
            return 2;
        }
        const auto family = build_family();
        const auto result = enumerate(family);
        const auto json = to_json(family, result);
        if (argc == 2) {
            std::ofstream output(argv[1], std::ios::binary);
            if (!output) throw std::runtime_error("cannot open output path");
            output << json;
        }
        std::cout << json;
        if (!result.sat && result.tested != 15033172ULL) {
            throw std::runtime_error("UNSAT result did not exhaust the domain");
        }
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "error: " << error.what() << '\n';
        return 1;
    }
}
