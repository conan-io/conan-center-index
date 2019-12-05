cmake_minimum_required(VERSION 2.8.12)

project(PackageTest)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_executable(example example.cpp)
set_property(TARGET example PROPERTY CXX_STANDARD 11)
target_link_libraries(example CONAN_PKG::sqlpp11)
