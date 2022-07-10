cmake_minimum_required(VERSION 3.1)
project(test_package C CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(tiny-aes-c REQUIRED CONFIG)

add_executable(test_package_c test_package.c)
add_executable(test_package_cpp test_package.cpp)

target_link_libraries(test_package_c tiny-aes-c::tiny-aes-c)
target_link_libraries(test_package_cpp tiny-aes-c::tiny-aes-c)
