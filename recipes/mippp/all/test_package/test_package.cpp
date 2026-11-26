#include <cstdlib>
#include <iostream>
#include <ranges>

#include "mippp/linear_expression.hpp"
#include "mippp/model_entities.hpp"
#include "mippp/version.hpp"

using namespace mippp::operators;

int main(void) {
    using Var = mippp::model_variable<int, double>;

    auto expr = 2.0 * Var(0) + Var(1) + 3.0;

    if (std::ranges::distance(expr.linear_terms()) != 2) return EXIT_FAILURE;
    if (expr.constant() != 3.0) return EXIT_FAILURE;

    std::cout << "MIP++ version: " << MIPPP_VERSION << std::endl;
    return EXIT_SUCCESS;
}
