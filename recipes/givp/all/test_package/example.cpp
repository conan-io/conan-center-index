// SPDX-FileCopyrightText: 2026 Arnaldo Mendes Pires Junior
// SPDX-License-Identifier: MIT

#include <iostream>
#include <vector>

#include <givp/givp.hpp>

int main() {
    // Simple sphere function minimization
    auto sphere = [](const std::vector<double> &x) {
        double s = 0.0;
        for (double v : x) {
            s += v * v;
        }
        return s;
    };

    std::vector<std::pair<double, double>> bounds(5, {-5.12, 5.12});
    givp::GivpConfig cfg;
    cfg.max_iterations = 20;
    cfg.seed = 42;

    auto result = givp::givp(sphere, bounds, cfg);

    if (!result.success) {
        std::cerr << "Optimization failed: " << result.message << '\n';
        return 1;
    }

    std::cout << "Sphere optimization successful.\n";
    std::cout << "Best value found: " << result.fun << '\n';
    std::cout << "Number of evaluations: " << result.nfev << '\n';

    if (result.fun < 1.0) {
        std::cout << "Result is excellent (< 1.0).\n";
        return 0;
    }

    std::cout << "Result is acceptable.\n";
    return 0;
}
