cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

find_package(tree-sitter-cpp REQUIRED CONFIG)

add_executable(${PROJECT_NAME} src/test_package.cc)
target_link_libraries(${PROJECT_NAME} PRIVATE tree-sitter-cpp::tree-sitter-cpp)
