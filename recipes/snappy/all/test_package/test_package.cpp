#include <cstdlib>
#include <string>
#include <iostream>
#include <snappy.h>

int main() {
    
    std::string input("Bincrafters");
    std::string output;

    const size_t result = snappy::Compress(input.c_str(), input.size(), &output);

    std::cout << input << " compressed (" << result << "): " << output << std::endl;   

    return EXIT_SUCCESS;
}
