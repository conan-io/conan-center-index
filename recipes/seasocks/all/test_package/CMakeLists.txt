cmake_minimum_required(VERSION 3.3)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(Seasocks REQUIRED)

add_executable(seasocks_test seasocks_test.cpp)
target_link_libraries(seasocks_test PRIVATE Seasocks::seasocks)
