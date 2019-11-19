cmake_minimum_required(VERSION 3.5)
project(PackageTest)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_executable(example example.cpp)
target_link_libraries(example CONAN_PKG::docopt.cpp)
set_property(TARGET example PROPERTY CMAKE_CXX_STANDARD 11)
set_property(TARGET example PROPERTY CMAKE_CXX_EXTENSIONS OFF)
