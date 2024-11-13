#include "hello-conan.h"
#include <vector>
#include <string>

int main() {
    hello_conan();

    std::vector<std::string> vec;
    vec.push_back("test_package");

    hello_conan_print_vector(vec);
}
