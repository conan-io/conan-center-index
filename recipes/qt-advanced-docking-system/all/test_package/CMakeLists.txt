cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)
add_executable(example example.cpp)

target_link_libraries(example CONAN_PKG::qt CONAN_PKG::qt-advanced-docking-system)
set_property(TARGET example PROPERTY CXX_STANDARD 11)
