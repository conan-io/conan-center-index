/*
From test_broadphase_dynamic_AABB_tree.cpp test in FCL test directory
*/

#include "fcl/common/types.h"
#include "fcl/geometry/shape/sphere.h"
#include "fcl/broadphase/broadphase_dynamic_AABB_tree.h"

#include <memory>
#include <vector>

int main() {
  auto sphere0 = std::make_shared<fcl::Sphered>(0.1);
  auto sphere1 = std::make_shared<fcl::Sphered>(0.2);
  fcl::CollisionObjectd object0(sphere0);
  fcl::CollisionObjectd object1(sphere1);
  const fcl::Vector3d position0(0.1, 0.2, 0.3);
  const fcl::Vector3d position1(0.11, 0.21, 0.31);

  // We will use `objects` to check the order of the two collision objects in
  // our callback function.
  //
  // We use std::vector that contains *pointers* to CollisionObjectd,
  // instead of std::vector that contains CollisionObjectd's.
  // Previously we used std::vector<fcl::CollisionObjectd>, and it failed the
  // Eigen alignment assertion on Win32. We also tried, without success, the
  // custom allocator:
  //     std::vector<fcl::CollisionObjectd,
  //                 Eigen::aligned_allocator<fcl::CollisionObjectd>>,
  // but some platforms failed to build.
  std::vector<fcl::CollisionObjectd*> objects = {&object0, &object1};
  std::vector<const fcl::Vector3d*> positions = {&position0, &position1};

  fcl::DynamicAABBTreeCollisionManager<double> dynamic_tree;
  for (int i = 0; i < static_cast<int>(objects.size()); ++i) {
    objects[i]->setTranslation(*positions[i]);
    objects[i]->computeAABB();
    dynamic_tree.registerObject(objects[i]);
  }

  // Pack the data for callback function.
  struct CallBackData {
    bool expect_object0_then_object1;
    std::vector<fcl::CollisionObjectd*>* objects;
  } data;
  data.expect_object0_then_object1 = false;
  data.objects = &objects;

  // This callback function tests the order of the two collision objects from
  // the dynamic tree against the `data`. We assume that the first two
  // parameters are always objects[0] and objects[1] in two possible orders,
  // so we can safely ignore the second parameter. We do not use the last
  // double& parameter, which specifies the distance beyond which the
  // pair of objects will be skipped.
  auto distance_callback = [](fcl::CollisionObjectd* a, fcl::CollisionObjectd*,
                              void* callback_data, double&) -> bool {
    // Unpack the data.
    auto data = static_cast<CallBackData*>(callback_data);
    const std::vector<fcl::CollisionObjectd*>& objects = *(data->objects);
    const bool object0_first = a == objects[0];
    // EXPECT_EQ(data->expect_object0_then_object1, object0_first);
    // TODO(DamrongGuoy): Remove the statement below when we solve the
    //  repeatability problem as mentioned in:
    //  https://github.com/flexible-collision-library/fcl/issues/368
    // Expect to switch the order next time.
    data->expect_object0_then_object1 = !data->expect_object0_then_object1;
    // Return true to stop the tree traversal.
    return true;
  };
  // We repeat update() and distance() many times.  Each time, in the
  // callback function, we check the order of the two objects.
  for (int count = 0; count < 8; ++count) {
    dynamic_tree.update();
    dynamic_tree.distance(&data, distance_callback);
  }

  return 0;
}
