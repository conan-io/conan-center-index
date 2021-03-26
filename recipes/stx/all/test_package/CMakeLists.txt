cmake_minimum_required(VERSION 3.8)
project(PackageTest LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(stx CONFIG REQUIRED)

add_executable(example example.cpp)
target_link_libraries(example PRIVATE stx::stx)
