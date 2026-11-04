#include <iostream>
#include <string>

#include "rapidhash.h"

int main() {
    std::string text = "Hello, rapidhash.";

    std::cout << rapidhash(text.data(), text.size()) << '\n';

    return 0;
}
