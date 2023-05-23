// From first_udp_ver0.cpp in tutorials of pagmo2

#include <pagmo/problem.hpp>
#include <pagmo/types.hpp>

#include <cmath>
#include <initializer_list>
#include <iostream>
#include <utility>

// Our simple example problem, version 0.
struct problem_v0 {
    // Implementation of the objective function.
    pagmo::vector_double fitness(const pagmo::vector_double &dv) const
    {
        return {dv[0] * dv[3] * (dv[0] + dv[1] + dv[2]) + dv[2]};
    }
    // Implementation of the box bounds.
    std::pair<pagmo::vector_double, pagmo::vector_double> get_bounds() const
    {
        return {{1., 1., 1., 1.}, {5., 5., 5., 5.}};
    }
};

int main()
{
    // Construct a pagmo::problem from our example problem.
    pagmo::problem p{problem_v0{}};

    // Getting its dimensions
    std::cout << "Calling the dimension getter: " << p.get_nx() << '\n';
    std::cout << "Calling the fitness dimension getter: " << p.get_nobj() << '\n';

    // Compute the value of the objective function
    // in the point (1, 2, 3, 4).
    std::cout << "Value of the objfun in (1, 2, 3, 4): " << p.fitness({1, 2, 3, 4})[0] << '\n';

    // Print p to screen.
    std::cout << p << "\n";

    return 0;
}
