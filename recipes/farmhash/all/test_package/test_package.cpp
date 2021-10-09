#include <farmhash.h>

#include <string>
#include <iostream>

int main() {

    std::string aString = "Conan";
    uint32_t hashResult;

    hashResult = util::Hash32(aString);

    std::cout << "Input string: " << aString << std::endl;
    std::cout << "Generated hash: " << hashResult << std::endl;

    return 0;
}
