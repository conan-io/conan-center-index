cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(qt-advanced-docking-system CONFIG REQUIRED)

add_executable(example example.cpp)
target_link_libraries(example qt-advanced-docking-system::qt-advanced-docking-system)
