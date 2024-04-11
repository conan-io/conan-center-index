// https://github.com/koide3/small_gicp/blob/ff8269ec09c9ddccff8358a4b7cc5e4c5fda134f/src/example/03_registration_template.cpp
// SPDX-FileCopyrightText: Copyright 2024 Kenji Koide
// SPDX-License-Identifier: MIT

/// @brief Basic point cloud registration example with small_gicp::align()
#include <iostream>
#include <small_gicp/benchmark/read_points.hpp>
#include <small_gicp/registration/registration_helper.hpp>

#include <small_gicp/ann/kdtree_omp.hpp>
#ifdef WITH_TBB
#include <small_gicp/ann/kdtree_tbb.hpp>
#endif

using namespace small_gicp;

/// @brief Most basic registration example.
void example1(const std::vector<Eigen::Vector4f>& target_points, const std::vector<Eigen::Vector4f>& source_points) {
  RegistrationSetting setting;
  setting.num_threads = 4;                    // Number of threads to be used
  setting.downsampling_resolution = 0.25;     // Downsampling resolution
  setting.max_correspondence_distance = 1.0;  // Maximum correspondence distance between points (e.g., trimming threshold)

  Eigen::Isometry3d init_T_target_source = Eigen::Isometry3d::Identity();
  RegistrationResult result = align(target_points, source_points, init_T_target_source, setting);

  std::cout << "--- T_target_source ---" << std::endl << result.T_target_source.matrix() << std::endl;
  std::cout << "converged:" << result.converged << std::endl;
  std::cout << "error:" << result.error << std::endl;
  std::cout << "iterations:" << result.iterations << std::endl;
  std::cout << "num_inliers:" << result.num_inliers << std::endl;
  std::cout << "--- H ---" << std::endl << result.H << std::endl;
  std::cout << "--- b ---" << std::endl << result.b.transpose() << std::endl;
}

int main(int argc, char** argv) {
  std::vector<Eigen::Vector4f> target_points = {
    {1.0f, 2.0f, 3.0f, 1.0f},
    {4.0f, 5.0f, 6.0f, 1.0f},
    {7.0f, 8.0f, 9.0f, 1.0f},
    {10.0f, 11.0f, 12.0f, 1.0f},
    {13.0f, 14.0f, 15.0f, 1.0f},
    {16.0f, 17.0f, 18.0f, 1.0f},
    {19.0f, 20.0f, 21.0f, 1.0f},
    {22.0f, 23.0f, 24.0f, 1.0f}
  };
  std::vector<Eigen::Vector4f> source_points = {
    {1.1f, 2.1f, 3.2f, 1.0f},
    {4.2f, 4.9f, 6.1f, 1.0f},
    {6.9f, 8.2f, 9.1f, 1.0f},
    {10.2f, 10.8f, 12.2f, 1.0f},
    {13.1f, 14.0f, 15.2f, 1.0f},
    {15.9f, 17.2f, 18.1f, 1.0f},
    {19.2f, 20.1f, 21.2f, 1.0f},
    {22.1f, 23.1f, 24.2f, 1.0f}
  };

  example1(target_points, source_points);

  // test that these compile and link
  KdTreeOMP<PointCloud>::Ptr kdtree_omp;
#ifdef WITH_TBB
  KdTreeTBB<PointCloud>::Ptr kdtree_tbb;
#endif

  return 0;
}
