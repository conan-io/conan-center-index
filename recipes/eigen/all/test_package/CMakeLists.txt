cmake_minimum_required(VERSION 3.5)
project(test_package LANGUAGES CXX)

find_package(Eigen3 REQUIRED CONFIG)

message(STATUS "Eigen versions:")

message(STATUS "EIGEN3_VERSION_MAJOR: ${EIGEN3_VERSION_MAJOR}")
message(STATUS "EIGEN3_VERSION_MINOR: ${EIGEN3_VERSION_MINOR}")
message(STATUS "EIGEN3_VERSION_PATCH: ${EIGEN3_VERSION_PATCH}")

message(STATUS "Eigen3_VERSION_MAJOR: ${Eigen3_VERSION_MAJOR}")
message(STATUS "Eigen3_VERSION_MINOR: ${Eigen3_VERSION_MINOR}")
message(STATUS "Eigen3_VERSION_PATCH: ${Eigen3_VERSION_PATCH}")

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE Eigen3::Eigen)
