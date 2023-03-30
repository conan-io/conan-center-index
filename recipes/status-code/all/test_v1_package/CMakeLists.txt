cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

# Just a workaround to not supprt the deprecated generators while passing the 1.x hooks
find_package(status-code REQUIRE CONFIG)
add_library(status-code::status-code ALIAS status-code::hl)

add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/../test_package/
                 ${CMAKE_CURRENT_BINARY_DIR}/test_package/)
