cmake_minimum_required(VERSION 3.1)
project(PackageTest)

set(CMAKE_CXX_STANDARD 11)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(icc REQUIRED)

add_executable(example example.cpp)
target_link_libraries(example PRIVATE icc::icc)
