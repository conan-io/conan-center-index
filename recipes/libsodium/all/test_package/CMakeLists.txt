cmake_minimum_required(VERSION 3.0)
project(Example CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_executable(example test.cpp)
target_link_libraries(example CONAN_PKG::libsodium)
