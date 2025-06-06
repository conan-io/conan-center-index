#include "hpp/fcl/math/transform.h"
#include "hpp/fcl/mesh_loader/loader.h"
#include "hpp/fcl/BVH/BVH_model.h"
#include "hpp/fcl/collision.h"
#include "hpp/fcl/collision_data.h"
#include <iostream>
#include <memory>

// Function to load a convex mesh from a `.obj`, `.stl` or `.dae` file.
//
// This function imports the object inside the file as a BVHModel, i.e. a point cloud
// which is hierarchically transformed into a tree of bounding volumes.
// The leaves of this tree are the individual points of the point cloud
// stored in the `.obj` file.
// This BVH can then be used for collision detection.
//
// For better computational efficiency, we sometimes prefer to work with
// the convex hull of the point cloud. This insures that the underlying object
// is convex and thus very fast collision detection algorithms such as
// GJK or EPA can be called with this object.
// Consequently, after creating the BVH structure from the point cloud, this function
// also computes its convex hull.
std::shared_ptr<hpp::fcl::ConvexBase> loadConvexMesh(const std::string& file_name) {
  hpp::fcl::NODE_TYPE bv_type = hpp::fcl::BV_AABB;
  hpp::fcl::MeshLoader loader(bv_type);
  hpp::fcl::BVHModelPtr_t bvh = loader.load(file_name);
  bvh->buildConvexHull(true, "Qt");
  return bvh->convex;
}

int main() {
  // Create the hppfcl shapes.
  // Hppfcl supports many primitive shapes: boxes, spheres, capsules, cylinders, ellipsoids, cones, planes,
  // halfspace and convex meshes (i.e. convex hulls of clouds of points).
  // It also supports BVHs (bounding volumes hierarchies), height-fields and octrees.
  std::shared_ptr<hpp::fcl::Ellipsoid> shape1 = std::make_shared<hpp::fcl::Ellipsoid>(0.7, 1.0, 0.8);
  std::shared_ptr<hpp::fcl::ConvexBase> shape2 = loadConvexMesh("../path/to/mesh/file.obj");

  // Define the shapes' placement in 3D space
  hpp::fcl::Transform3f T1;
  T1.setQuatRotation(hpp::fcl::Quaternion3f::UnitRandom());
  T1.setTranslation(hpp::fcl::Vec3f::Random());
  hpp::fcl::Transform3f T2 = hpp::fcl::Transform3f::Identity();
  T2.setQuatRotation(hpp::fcl::Quaternion3f::UnitRandom());
  T2.setTranslation(hpp::fcl::Vec3f::Random());

  // Define collision requests and results.
  //
  // The collision request allows to set parameters for the collision pair.
  // For example, we can set a positive or negative security margin.
  // If the distance between the shapes is less than the security margin, the shapes
  // will be considered in collision.
  // Setting a positive security margin can be usefull in motion planning,
  // i.e to prevent shapes from getting too close to one another.
  // In physics simulation, allowing a negative security margin may be usefull to stabilize the simulation.
  hpp::fcl::CollisionRequest col_req;
  col_req.security_margin = 1e-1;
  // A collision result stores the result of the collision test (signed distance between the shapes,
  // witness points location, normal etc.)
  hpp::fcl::CollisionResult col_res;

  // Collision call
  hpp::fcl::collide(shape1.get(), T1, shape2.get(), T2, col_req, col_res);

  // We can access the collision result once it has been populated
  std::cout << "Collision? " << col_res.isCollision() << "\n";
  if (col_res.isCollision()) {
    hpp::fcl::Contact contact = col_res.getContact(0);
    // The penetration depth does **not** take into account the security margin.
    // Consequently, the penetration depth is the true signed distance which separates the shapes.
    // To have the distance which takes into account the security margin, we can simply add the two together.
    std::cout << "Penetration depth: " << contact.penetration_depth << "\n";
    std::cout << "Distance between the shapes including the security margin: " << contact.penetration_depth + col_req.security_margin << "\n";
    std::cout << "Witness point on shape1: " << contact.nearest_points[0].transpose() << "\n";
    std::cout << "Witness point on shape2: " << contact.nearest_points[1].transpose() << "\n";
    std::cout << "Normal: " << contact.normal.transpose() << "\n";
  }

  // Before calling another collision test, it is important to clear the previous results stored in the collision result.
  col_res.clear();

  return 0;
}
