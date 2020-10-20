cmake_minimum_required(VERSION 3.1)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(Qt5 CONFIG REQUIRED Core)

add_executable(example example.cpp)
target_link_libraries(example CONAN_PKG::kcodecs Qt5::Core)
