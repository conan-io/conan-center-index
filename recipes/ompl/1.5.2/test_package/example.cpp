#include <iostream>
#include <memory>

#include <ompl/base/spaces/RealVectorStateSpace.h>
#include <ompl/geometric/SimpleSetup.h>

int main() {
  auto stateSpace = std::make_shared<ompl::base::RealVectorStateSpace>(5);
  auto setup = std::make_shared <ompl::geometric::SimpleSetup>(stateSpace);
  std::cout << "ompl objects constructed successfully" << std::endl;

  return 0;
}