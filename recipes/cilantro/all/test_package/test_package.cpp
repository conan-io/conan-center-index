#include <cilantro/core/kd_tree.hpp>
#include <iostream>
#include <vector>

int main() {
    std::vector<Eigen::Vector3f> points;
    points.emplace_back(0, 0, 0);
    points.emplace_back(1, 1, 1);
    cilantro::KDTree3f<> tree(points);
    std::cout << "KDTree size: " << tree.getPointsMatrixMap().cols() << std::endl;
    return 0;
}
