#include <cstdlib>
#include <cstdlib>
#include <iostream>
#include <lift/lift.hpp>


int main() {
    std::cout << "lift status: " << lift::to_string(lift::lift_status::success) << std::endl;
    return EXIT_SUCCESS;
}
