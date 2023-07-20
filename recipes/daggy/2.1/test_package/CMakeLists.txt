cmake_minimum_required(VERSION 3.15)
project(DaggyPackageTest LANGUAGES CXX)

find_package(daggy REQUIRED CONFIG)

if (NOT CMAKE_CXX_STANDARD)
    set(CMAKE_CXX_STANDARD 17)
endif()
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(testcpp test.cpp)
target_link_libraries(testcpp daggy::daggy)
