cmake_minimum_required(VERSION 3.5)
project(PackageTest CXX)

set(CMAKE_CXX_STANDARD 11)

include(conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_executable(example example.cpp)
target_link_libraries(example CONAN_PKG::karchive CONAN_PKG::qt)
