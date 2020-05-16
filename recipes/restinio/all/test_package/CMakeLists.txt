cmake_minimum_required(VERSION 2.8.12)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_executable(example example.cpp)
set_target_properties(example PROPERTIES CXX_STANDARD 14)
target_link_libraries(example CONAN_PKG::restinio)
