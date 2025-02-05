#include <fcl/narrowphase/distance.h>

#include <memory>
#include <iostream>

int main() {
  using namespace fcl;
  std::shared_ptr<CollisionGeometry<double>> box_geometry_1(new Box<double>());
  std::shared_ptr<CollisionGeometry<double>> box_geometry_2(new Box<double>());
  CollisionObject<double> box_object_1(box_geometry_1);
  CollisionObject<double> box_object_2(box_geometry_2);
  DistanceRequest<double> request;
  DistanceResult<double> result;
  std::cout << "Distance: " << distance<double>(&box_object_1, &box_object_2, request, result) << std::endl;
}
