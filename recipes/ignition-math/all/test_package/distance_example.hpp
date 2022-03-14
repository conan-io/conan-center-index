#include <iostream>
#include <ignition/math.hh>


void run_distance_example()
{
    std::cout << "\n=======================================\n"
              << "\trunning distance example\n"
              << "=======================================\n";

    ignition::math::Vector3d point1{1, 3, 5};
    ignition::math::Vector3d point2{2, 4, 6};

    double distance = point1.Distance(point2);
    std::cout << "Distance from (" << point1 << ") to " 
              << point2 << " is " << distance << std::endl;
}
