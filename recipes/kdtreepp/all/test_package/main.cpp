#include <kdtreepp.hpp>
#include <vector>
int main() {
  using Point = Eigen::Vector3d;
  std::vector<Point> points{Point::Zero(), Point::Ones()};
  const auto tree = kdtreepp::MakeEigenKdTreeNode<double, 3>(
      points.begin(), points.end(), [](const Point& p) { return p; },
      [](const Point& p) { return p; });
  int count = 0;
  tree.visit([](const auto&) { return true; }, [&](const Point&) { ++count; });
  return count == 2 ? 0 : 1;
}
