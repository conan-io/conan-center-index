cmake_minimum_required(VERSION 3.1.2)
project(PackageTest CXX)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_EXTENSIONS OFF)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_executable(example example.cpp)
target_link_libraries(example CONAN_PKG::enum-flags)
