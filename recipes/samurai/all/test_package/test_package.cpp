#include <cstdlib>
#include <iostream>
#include "samurai/uniform_mesh.hpp"


int main(void) {
    constexpr std::size_t dim = 2;
    using Config = samurai::UniformConfig<dim>;

    samurai::Box<double, dim> box({-1}, {1});
    samurai::UniformMesh<Config> umesh{box, 10};

    return EXIT_SUCCESS;
}
