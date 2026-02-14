#include <tmd/TriangleMeshDistance.h>

#include <cstdio>
#include <vector>
#include <array>

int main(int argc, char **argv) {

  std::vector<std::array<double, 3>> vertices = {{{0, 0, 0}, {1, 0, 0}, {0, 1, 0}}};
  std::vector<std::array<int, 3>> triangles = {{{0, 1, 2}}};

  tmd::TriangleMeshDistance mesh_distance(vertices, triangles);

  std::array<double, 3> query_point = {0, 0, 1};
  auto result = mesh_distance.signed_distance(query_point);

  printf("Computed distance: %f\n", result.distance);

  return 0;
}
