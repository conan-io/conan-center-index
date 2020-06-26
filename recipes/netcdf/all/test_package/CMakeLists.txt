cmake_minimum_required(VERSION 2.8.0 FATAL_ERROR)
project (netcdf_example)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_executable(example
    ${CMAKE_SOURCE_DIR}/example.c
)
target_link_libraries(example CONAN_PKG::netcdf)
