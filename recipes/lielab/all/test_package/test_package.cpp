#include <cstdlib>
#include <iostream>
#include <Lielab.hpp>


int main(void) {
    using Lielab::domain::so;
    using Lielab::domain::SO;
    using Lielab::functions::exp;
    using Lielab::functions::Ad;

    const so u = so::from_vector({1.0, 0.0, 0.0});
    const so v = so::from_vector({0.0, 1.0, 0.0});
    const so w = so::from_vector({0.0, 0.0, 1.0});

    const SO g = exp(v);
    const so x = Ad(g, u);

    std::cout << "Lielab v" << Lielab::VERSION << std::endl;
    std::cout << Lielab::AUTHOR << std::endl;
    std::cout << Lielab::LOCATION << std::endl;

    return EXIT_SUCCESS;
}