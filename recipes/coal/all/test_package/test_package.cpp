#include "coal/BVH/BVH_model.h"
#include "coal/collision.h"
#include "coal/collision_data.h"
#include "coal/math/transform.h"
#include "coal/mesh_loader/loader.h"
#include <iostream>
#include <memory>

std::shared_ptr<coal::ConvexBase> loadConvexMesh(const std::string &file_name) {
  coal::NODE_TYPE bv_type = coal::BV_AABB;
  coal::MeshLoader loader(bv_type);
  coal::BVHModelPtr_t bvh = loader.load(file_name);
  bvh->buildConvexHull(true, "Qt");
  return bvh->convex;
}

int main() {
  std::shared_ptr<coal::Ellipsoid> shape1 =
      std::make_shared<coal::Ellipsoid>(0.7, 1.0, 0.8);
  std::shared_ptr<coal::Ellipsoid> shape2 =
      std::make_shared<coal::Ellipsoid>(1.0, 2.0, 3.8);

  coal::Transform3s T1;
  T1.setQuatRotation(coal::Quaternion3f::UnitRandom());
  T1.setTranslation(coal::Vec3s::Random());
  coal::Transform3s T2 = coal::Transform3s::Identity();
  T2.setQuatRotation(coal::Quaternion3f::UnitRandom());
  T2.setTranslation(coal::Vec3s::Random());

  coal::CollisionRequest col_req;
  col_req.security_margin = 1e-1;
  coal::CollisionResult col_res;

  coal::collide(shape1.get(), T1, shape2.get(), T2, col_req, col_res);
  std::cout << "Collision? " << col_res.isCollision() << "\n";
  if (col_res.isCollision()) {
    coal::Contact contact = col_res.getContact(0);
    std::cout << "Penetration depth: " << contact.penetration_depth << "\n";
    std::cout << "Distance between the shapes including the security margin: "
              << contact.penetration_depth + col_req.security_margin << "\n";
    std::cout << "Witness point on shape1: "
              << contact.nearest_points[0].transpose() << "\n";
    std::cout << "Witness point on shape2: "
              << contact.nearest_points[1].transpose() << "\n";
    std::cout << "Normal: " << contact.normal.transpose() << "\n";
  }

  col_res.clear();

  return 0;
}
