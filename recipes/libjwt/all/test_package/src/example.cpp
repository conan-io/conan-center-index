#include "libjwt.h"
#include <vector>
#include <string>

int main() {
    libjwt();

    std::vector<std::string> vec;
    vec.push_back("test_package");

    libjwt_print_vector(vec);
}
