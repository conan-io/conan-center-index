cmake_minimum_required(VERSION 3.15.0)
project(DaggyPackageTest LANGUAGES CXX)

find_package(DaggyCore CONFIG REQUIRED)

add_executable(testcpp test.cpp)
target_sources(testcpp PRIVATE test.cpp)

target_link_libraries(testcpp daggy::DaggyCore)
