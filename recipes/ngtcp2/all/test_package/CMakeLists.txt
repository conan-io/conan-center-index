cmake_minimum_required(VERSION 3.20)
project(test_package CXX)

find_package("ngtcp2" REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} ngtcp2::ngtcp2)
