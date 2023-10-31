cmake_minimum_required(VERSION 3.1.2)
project(test_package CXX)

find_package(iconfontcppheaders REQUIRED CONFIG)

add_executable(${CMAKE_PROJECT_NAME} test_package.cpp)
target_link_libraries(${CMAKE_PROJECT_NAME} PRIVATE iconfontcppheaders::iconfontcppheaders)
