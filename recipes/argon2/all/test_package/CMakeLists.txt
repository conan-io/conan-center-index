cmake_minimum_required(VERSION 3.1.2)
project(Argon2Test CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(argon2 REQUIRED)

add_executable(argon2-test argon2-test.cpp)

target_link_libraries(argon2-test argon2::argon2)
