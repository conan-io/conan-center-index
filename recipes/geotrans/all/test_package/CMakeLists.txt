cmake_minimum_required(VERSION 3.1)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)
include(${CMAKE_BINARY_DIR}/conan_paths.cmake)

find_package(geotrans REQUIRED COMPONENTS dtcc ccs)

add_executable(example example.cpp)
target_link_libraries(example geotrans::dtcc geotrans::ccs)
