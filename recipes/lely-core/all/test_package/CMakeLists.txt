cmake_minimum_required(VERSION 3.2)
project(test_package)

find_package(lely-core REQUIRED)

add_executable("${PROJECT_NAME}" test_package.cpp)
target_link_libraries("${PROJECT_NAME}" PRIVATE lely-core::lely-core)
target_compile_features("${PROJECT_NAME}" PRIVATE cxx_std_11)
