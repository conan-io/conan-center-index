#include <cstdlib>
#include <iostream>
#include "ApprovalTests.hpp"
#include "utilities/Grid.h"


int main(void) {
    std::cout << ApprovalTests::StringMaker::toString(42) << " is the answer."<< std::endl;
    return EXIT_SUCCESS;
}
