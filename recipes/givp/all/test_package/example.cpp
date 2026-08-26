// SPDX-FileCopyrightText: 2026 Arnaldo Mendes Pires Junior
// SPDX-License-Identifier: MIT

#include <utility>
#include <vector>

#include <givp/givp.hpp>

int main() {
    const auto sphere = [](const std::vector<double>& values) {
        double sum = 0.0;
        for (const double value : values) {
            sum += value * value;
        }
        return sum;
    };

    const std::vector<std::pair<double, double>> bounds(3, {-5.0, 5.0});
    givp::GivpConfig config;
    config.max_iterations = 10;
    config.seed = 42;

    const auto result = givp::givp(sphere, bounds, config);
    return result.success ? 0 : 1;
}
