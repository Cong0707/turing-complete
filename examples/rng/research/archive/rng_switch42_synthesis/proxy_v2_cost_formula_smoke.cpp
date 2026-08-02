#include "proxy_v2_cost_formula.hpp"

int main() {
    const std::vector<std::uint64_t> targets{0x3, 0x7, 0xf, 0x1f};
    const auto weight = rng_proxy_v2::weight_estimate(targets, 10);
    const auto pair = rng_proxy_v2::pair_estimate(targets, 10);
    return weight.unsupported || pair.unsupported;
}
