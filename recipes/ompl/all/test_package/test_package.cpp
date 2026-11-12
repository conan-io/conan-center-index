#include <iostream>
#include <memory>

#include <ompl/base/SpaceInformation.h>
#include <ompl/base/spaces/special/SphereStateSpace.h>

int main() {
    auto space = std::make_shared<ompl::base::SphereStateSpace>(1.0);
    ompl::base::SpaceInformation si(space);
    si.setStateValidityChecker([](const ompl::base::State *) { return true; });
    si.setup();

    std::cout << "ompl test_package: space dim=" << space->getDimension()
              << " state dim=" << si.getStateDimension() << std::endl;
    return 0;
}
