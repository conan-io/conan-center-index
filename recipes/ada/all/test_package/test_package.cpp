#include <iostream>

#include "ada.h"

int main() {
    ada::result<ada::url_aggregator> url = ada::parse<ada::url_aggregator>("https://www.google.com");
    if(!url) {
        return 1;
    }

    std::cout << url->get_host() << std::endl;

    return 0;
}
