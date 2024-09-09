cmake_minimum_required(VERSION 3.10)
project(test_package LANGUAGES CXX)

find_package(CGAL REQUIRED)
find_package(Eigen3 REQUIRED)
include(CGAL_Eigen3_support)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE CGAL::CGAL)
target_link_libraries(${PROJECT_NAME} PRIVATE CGAL::Eigen3_support)
