#include <small_gicp/points/point_cloud.hpp>
#include <small_gicp/ann/kdtree_omp.hpp>
#ifdef WITH_TBB
#include <small_gicp/ann/kdtree_tbb.hpp>
#endif

using namespace small_gicp;

int main() {
  std::vector<Eigen::Vector4f> target_points = {
    {1.0f, 2.0f, 3.0f, 1.0f},
    {4.0f, 5.0f, 6.0f, 1.0f},
    {7.0f, 8.0f, 9.0f, 1.0f},
  };
  auto target = std::make_shared<PointCloud>(target_points);

  const int num_threads = 1;
  std::make_shared<KdTree<PointCloud>>(target, KdTreeBuilderOMP(num_threads));

#ifdef WITH_TBB
  std::make_shared<KdTree<PointCloud>>(target, KdTreeBuilderTBB());
#endif

}
