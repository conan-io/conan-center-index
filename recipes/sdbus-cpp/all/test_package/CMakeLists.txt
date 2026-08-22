cmake_minimum_required(VERSION 3.15)
project(PackageTest LANGUAGES CXX)

find_package(sdbus-c++ REQUIRED)

add_executable(example example.cpp)
target_link_libraries(example SDBusCpp::sdbus-c++)
