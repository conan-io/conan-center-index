cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX C)

find_package(OpenMP CONFIG REQUIRED)

add_executable(test_package_cxx test_package.cpp)
target_link_libraries(test_package_cxx OpenMP::OpenMP_CXX)

add_executable(test_package_c test_package.c)
target_link_libraries(test_package_c OpenMP::OpenMP_C)
