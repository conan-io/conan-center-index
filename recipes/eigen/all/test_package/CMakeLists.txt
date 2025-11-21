cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(Eigen3 REQUIRED CONFIG)

message(STATUS "Eigen3 version: ${Eigen3_VERSION}")
message(STATUS "Eigen3 major version: ${Eigen3_VERSION_MAJOR}")
message(STATUS "Eigen3 minor version: ${Eigen3_VERSION_MINOR}")
message(STATUS "Eigen3 patch version: ${Eigen3_VERSION_PATCH}")
message(STATUS "Eigen3 version string: ${Eigen3_VERSION_STRING}")


add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE Eigen3::Eigen)
