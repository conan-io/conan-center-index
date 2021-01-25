cmake_minimum_required(VERSION 3.1)
project(PackageTest C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(pupnp REQUIRED)

add_executable(example main.c)
target_link_libraries(example pupnp::pupnp)
set_target_properties(example PROPERTIES C_STANDARD 99)
