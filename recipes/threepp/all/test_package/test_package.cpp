#include <cstdlib>
#include <iostream>
#include <threepp/threepp.hpp>
#include <threepp/utils/StringUtils.hpp>

int main() {    
    std::cout << "Treecpp Test Package: " << threepp::utils::parseInt("42") << std::endl;
    return EXIT_SUCCESS;
}
