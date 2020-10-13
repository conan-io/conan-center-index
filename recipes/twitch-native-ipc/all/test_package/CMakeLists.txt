cmake_minimum_required(VERSION 2.8.11)
project(PackageTest C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)

add_executable(example example.c)
target_link_libraries(example ${CONAN_LIBS})
