cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(iceoryx REQUIRED CONFIG)

add_subdirectory(single_process)
add_subdirectory(icedelivery)
add_subdirectory(icedelivery_in_c)
