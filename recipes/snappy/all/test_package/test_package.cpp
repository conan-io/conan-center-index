#include <snappy.h>

#include <cstdlib>
#include <string>
#include <iostream>

int main() {
    std::string input("conan-enter-index");
    std::string output;

    const size_t result = snappy::Compress(input.c_str(), input.size(), &output);

    std::cout << input << " compressed (" << result << "): " << output << std::endl;

    return EXIT_SUCCESS;
}
