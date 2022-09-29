cmake_minimum_required(VERSION 3.8)

project(test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(c-blosc2 REQUIRED CONFIG)

add_executable(${PROJECT_NAME} ../test_package/test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE c-blosc2::c-blosc2)
