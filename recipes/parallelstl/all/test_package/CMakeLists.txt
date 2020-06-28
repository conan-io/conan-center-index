cmake_minimum_required(VERSION 3.4.3)
project(ParallelSTLPackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_executable(example example.cpp)
find_package(ParallelSTL)
target_link_libraries(example PUBLIC ParallelSTL::ParallelSTL)
