cmake_minimum_required(VERSION 3.6)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(armadillo REQUIRED)

add_executable(example example.cpp)
target_link_libraries(example armadillo::armadillo)
set_property(TARGET example PROPERTY CXX_STANDARD 11)
