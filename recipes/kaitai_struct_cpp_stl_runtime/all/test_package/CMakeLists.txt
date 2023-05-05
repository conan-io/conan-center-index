cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES CXX)

find_package(kaitai_struct_cpp_stl_runtime REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE kaitai_struct_cpp_stl_runtime::kaitai_struct_cpp_stl_runtime)
