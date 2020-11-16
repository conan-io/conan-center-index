cmake_minimum_required(VERSION 3.1.2)
project(Argon2Test CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_executable(argon2-test argon2-test.cpp)
target_link_libraries(argon2-test CONAN_PKG::argon2)
