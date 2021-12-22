#include <opengv/math/roots.hpp>

#include <vector>
#include <iostream>

int main() {

    std::vector<double> poly {1.0, -2.0, -5.0, 6.0};
    std::vector<double> computed_roots = opengv::math::o3_roots(poly);
    std::vector<double> expected_roots {-2.0, 3.0, 1.0};

    std::cout << "Computed roots: ";
    for (auto i = computed_roots.begin(); i != computed_roots.end(); ++i)
        std::cout << *i << ' ';
    std::cout << std::endl;

    std::cout << "Expected roots: ";
    for (auto i = expected_roots.begin(); i != expected_roots.end(); ++i)
        std::cout << *i << ' ';
    std::cout << std::endl;

    if (computed_roots != expected_roots) {
        std::cout << "The calculated roots do not match the expected ones" <<  std::endl;
        return 1;
    }

    std::cout << "Success" <<  std::endl;
    return 0;

}
