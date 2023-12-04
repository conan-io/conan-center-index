cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(quickfix REQUIRED CONFIG)

add_executable(executor ${PROJECT_SOURCE_DIR}/executor.cpp)
target_link_libraries(executor PRIVATE quickfix::quickfix)
