#include "upa/url.h"
#include <iostream>

int main() {
    try {
        upa::url url{ "https://upa-url.github.io/docs/", "about:blank" };
        std::cout << url.href() << '\n';
        return 0;
    }
    catch (...) {
        return 1;
    }
}
