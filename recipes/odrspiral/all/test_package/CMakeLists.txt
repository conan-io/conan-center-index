cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

find_package(odrspiral CONFIG REQUIRED)

add_executable(test_odrspiral main.cpp)
target_link_libraries(test_odrspiral odrspiral::odrspiral)
