cmake_minimum_required(VERSION 3.15)
project(test_package)

find_package(rdma-core REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE rdma-core::libibverbs)
