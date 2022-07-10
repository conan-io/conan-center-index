#include <fdeep/fdeep.hpp>
#include <iostream>

int main()
{
    const fdeep::tensor t(
        fdeep::tensor_shape(static_cast<std::size_t>(4)),
        fdeep::float_vec{1, 2, 3, 4});
    std::cout << fdeep::show_tensor(t) << std::endl;
}
