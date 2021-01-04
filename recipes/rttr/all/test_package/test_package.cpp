#include <cstdlib>
#include <iostream>
#include <vector>

#include <rttr/type>

using dblvec = std::vector<double>;

int main()
{
    auto type = rttr::type::get<dblvec>();
    std::cout << "type name: " << type.get_name() << std::endl;;
    return EXIT_SUCCESS;
}
