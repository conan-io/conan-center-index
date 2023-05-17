
/**
 * @file test_package.cpp
 * @author ggulglia(gajendra.gulgulia@gmail.com)
 * @brief test examples to verify that conan recipe for ignition-math
 *        can be consumed
 */

#include <iostream>
#include <ignition/math/Angle.hh>
#include <ignition/math.hh>

int main(int argc, char** argv)
{
    std::cout << "hello world from ignition-math test_package\n";

    ignition::math::Vector3d point1{1, 3, 5};
    ignition::math::Vector3d point2{2, 4, 6};

    double distance = point1.Distance(point2);
    std::cout << "Distance from (" << point1 << ") to " 
              << point2 << " is " << distance << std::endl;
}
