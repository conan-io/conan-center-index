#include <ompl/base/SpaceInformation.h>
#include <ompl/base/spaces/RealVectorStateSpace.h>
#include <iostream>

int main() {
    // Construct a simple 3D state space
    auto space = std::make_shared<ompl::base::RealVectorStateSpace>(3);

    // Construct a space information instance for this state space
    ompl::base::SpaceInformation si(space);

    // Simple check to ensure library loaded and objects can be created
    std::cout << "OMPL Test: State space dimension is " << space->getDimension() << std::endl;

    return 0;
}
