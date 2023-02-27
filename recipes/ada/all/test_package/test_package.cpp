#include <iostream>

#include "ada.h"

int main() {
    ada::result url = ada::parse("https://www.google.com");
    if(not url) {
        return 1;
    }

    std::cout << url->get_host() << std::endl;

    return 0;
}
