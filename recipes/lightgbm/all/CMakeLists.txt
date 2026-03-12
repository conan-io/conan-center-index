cmake_minimum_required(VERSION 3.15)
project(cmake_wrapper LANGUAGES CXX)

find_package(Eigen3 REQUIRED CONFIG)
find_package(fast_double_parser REQUIRED CONFIG)
find_package(fmt REQUIRED CONFIG)

add_subdirectory(src)

target_link_libraries(lightgbm_objs PRIVATE Eigen3::Eigen fast_double_parser::fast_double_parser fmt::fmt)
target_link_libraries(lightgbm_capi_objs PRIVATE Eigen3::Eigen fast_double_parser::fast_double_parser fmt::fmt)
