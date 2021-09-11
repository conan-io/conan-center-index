cmake_minimum_required(VERSION 3.1)
project(PackageTest CXX)

set(CMAKE_CXX_STANDARD 17)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(wasmtime-cpp REQUIRED)

add_executable(example example.cpp)
target_link_libraries(example PRIVATE wasmtime-cpp::wasmtime-cpp)
target_compile_definitions(example PUBLIC WASMTIME_EXAMPLES_PATH="${CMAKE_SOURCE_DIR}")
