
/**
 * @file test_package.cpp
 * @author ggulglia(gajendra.gulgulia@gmail.com)
 * @brief test examples to verify that conan recipe for ignition-math
 *        can be consumed
 */

#include "angle_example.hpp"
#include "distance_example.hpp"

int main(int argc, char** argv)
{
    std::cout << "hello world from ignition-math test_package\n";

    run_angle_example();
    run_distance_example();
}
