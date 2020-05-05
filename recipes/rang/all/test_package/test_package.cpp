#include <iostream>

#include "rang.hpp"

int main() {
    std::cout << std::endl
         << rang::style::reset << rang::bg::green << rang::fg::gray << rang::style::bold
         << " Rang works! " << rang::bg::reset << rang::fg::reset << rang::style::reset << '\n'
         << std::endl;
    return 0;
}
