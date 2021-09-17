#include <farmhash.h>

#include <string>
#include <iostream>

int main() {

    std::string aString = "Conan";
    uint32_t hashResult;
    uint32_t expectedHash = 2608518170;

    hashResult = util::Hash32(aString);

    if (hashResult != expectedHash) {
        std::cout << "The calculated hash doesn't match the expected value." << std::endl;
        std::cout << "Generated hash: " << hashResult << std::endl;
        std::cout << "Expected hash: " << expectedHash << std::endl;
        return 1;
    }

    std::cout << "Input string: " << aString << std::endl;
    std::cout << "Generated hash: " << hashResult << std::endl;

    return 0;
}
