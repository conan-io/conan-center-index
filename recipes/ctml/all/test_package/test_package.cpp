#include <iostream>

#include "ctml.hpp"

int main() {
    CTML::Node node("div#first section#second article#third");

    std::cout << node.ToString() << std::endl;

    return 0;
}
