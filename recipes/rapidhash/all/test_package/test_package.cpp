#include <iostream>
#include <string_view>

#include "rapidhash.h"

int main() {
    std::string_view text = "Hello, rapidhash.";

    std::cout << rapidhash(text.data(), text.size()) << '\n';

    return 0;
}
