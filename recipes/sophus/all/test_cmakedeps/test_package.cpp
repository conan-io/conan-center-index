#define _USE_MATH_DEFINES
#include <iostream>
#include <sophus/se3.hpp>

int main() {
  Sophus::Matrix4d random_se3 = Sophus::SE3d::exp(Sophus::Vector6d::Random()).matrix();
  std::cout << "Random SE(3) matrix:\n" << random_se3 << std::endl;

#ifdef SOPHUS_FMT_PRINT
  SOPHUS_FMT_PRINT("Sophus fmt check: {}, {}. (If works should be: 20.0, true)", 20.0, true);
#endif

  std::cout << "Sophus uses EIGEN_VERSION: " << EIGEN_WORLD_VERSION << "." << EIGEN_MAJOR_VERSION << "." << EIGEN_MINOR_VERSION << std::endl;

  return 0;
}
