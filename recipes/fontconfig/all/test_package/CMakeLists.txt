cmake_minimum_required(VERSION 3.1)
project(PackageTest C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(Fontconfig REQUIRED)

add_executable(example example.c)
target_link_libraries(example Fontconfig::Fontconfig)
set_target_properties(example PROPERTIES C_STANDARD 99)

