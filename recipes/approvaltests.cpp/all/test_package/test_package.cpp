#include <cstdlib>
#include <iostream>
#include "ApprovalTests.hpp"


int main(void) {
    std::cout << ApprovalTests::StringMaker::toString(42) << ApprovalTests::Grid::print(1, 1, " is the answer.")<< std::endl;
    return EXIT_SUCCESS;
}
