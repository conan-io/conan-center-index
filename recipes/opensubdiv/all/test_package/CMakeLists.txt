cmake_minimum_required(VERSION 3.1)
project(PackageTest CXX)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)

add_executable(example example.cpp)
target_link_libraries(example osdCPU)
