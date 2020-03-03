cmake_minimum_required(VERSION 2.8.12)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_executable(main main.cpp)
target_link_libraries(main CONAN_PKG::cs_libguarded)
set_property(TARGET main PROPERTY CXX_STANDARD 11)
