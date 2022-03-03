#include <cstdlib>
#include <iostream>
#include "ApprovalTests.hpp"


int main(void) {
    std::cout << ApprovalTests::StringMaker::toString(42) << " is the answer."<< std::endl;
    return EXIT_SUCCESS;
}