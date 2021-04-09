cmake_minimum_required(VERSION 3.1)
project(PackageTest C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(ldns CONFIG REQUIRED)

add_executable(example example.c)
target_link_libraries(example ldns::ldns)
