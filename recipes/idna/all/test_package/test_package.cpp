#include <iostream>
#include <string_view>

#include "idna.h"

int main(void) {
    std::string_view input = reinterpret_cast<const char*>(u8"meßagefactory.ca"); // non-empty UTF-8 string, must be percent decoded
    std::string idna_ascii = ada::idna::to_ascii(input);
    if(idna_ascii.empty()) {
        // There was an error.
    }
    std::cout << idna_ascii << std::endl;
    // outputs 'xn--meagefactory-m9a.ca' if the input is u8"meßagefactory.ca"
}
