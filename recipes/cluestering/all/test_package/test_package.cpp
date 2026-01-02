
#include <CLUEstering/CLUEstering.hpp>
#include <algorithm>

constexpr auto kNdim = 2u;

int main() {
  // Obtain the queue, which is used for allocations and kernel launches.
  auto queue = clue::get_queue(0u);

  const auto size = 1000;
  std::vector<float> coords(size * kNdim);
  std::generate(coords.begin(), coords.end(), []() {
    return static_cast<float>(std::rand()) / RAND_MAX * 100.f;
  });
  std::vector<float> weights(size, 1.f);
  std::vector<int> labels(size);

  // Allocate the points on the host and device.
  clue::PointsHost<kNdim> h_points(queue, size, coords, weights, labels);
  clue::PointsDevice<kNdim> d_points(queue, size);

  // Define the parameters for the clustering and construct the clusterer.
  const float dc = 20.f, rhoc = 10.f, outlier = 20.f;
  clue::Clusterer<kNdim> algo(queue, dc, rhoc, outlier);

  // Launch the clustering
  // The results will be stored in the `clue::PointsHost` object
  algo.make_clusters(queue, h_points, d_points);
}
