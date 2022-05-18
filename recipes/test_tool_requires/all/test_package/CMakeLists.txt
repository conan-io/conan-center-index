cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(test_tool_requires CONFIG REQUIRED)

add_executable(example src/example.cpp)
target_link_libraries(example test_tool_requires::test_tool_requires)
