cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

find_package(glog REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} glog::glog)
