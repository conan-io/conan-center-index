cmake_minimum_required(VERSION 3.12)

project(PackageTest CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED True)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(libqasm CONFIG REQUIRED)

add_executable(example src/example.cpp)
target_link_libraries(example libqasm::libqasm)
target_compile_features(example PUBLIC cxx_std_20)
