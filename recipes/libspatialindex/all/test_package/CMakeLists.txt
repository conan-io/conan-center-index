cmake_minimum_required(VERSION 3.8)
project(test_package)

find_package(libspatialindex REQUIRED CONFIG)

add_executable(test_package_c test_package.c)
target_link_libraries(test_package_c PRIVATE libspatialindex::spatialindex_c)

add_executable(test_package_cpp test_package.cpp)
target_link_libraries(test_package_cpp PRIVATE libspatialindex::spatialindex)
target_compile_features(test_package_cpp PRIVATE cxx_std_11)
