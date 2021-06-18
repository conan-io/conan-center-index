cmake_minimum_required(VERSION 3.1)
project(PackageTest CXX)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup(TARGETS)

find_package(jwt-cpp REQUIRED)

add_executable(example example.cpp)
set_property(TARGET example PROPERTY CXX_STANDARD 11)

target_link_libraries(example jwt-cpp::jwt-cpp CONAN_PKG::picojson)
