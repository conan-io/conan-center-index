cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(kcp REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} kcp::kcp)
set_target_properties(${PROJECT_NAME} PROPERTIES CXX_STANDARD 11)
