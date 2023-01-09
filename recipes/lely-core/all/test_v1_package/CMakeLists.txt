cmake_minimum_required(VERSION 3.2)
project(test_package)

find_package(lely-core REQUIRED)

add_executable("${PROJECT_NAME}" ${CMAKE_SOURCE_DIR}/../test_package/test_package.cpp)
target_link_libraries("${PROJECT_NAME}" PRIVATE lely-core::lely-core)
