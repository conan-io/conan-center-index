cmake_minimum_required(VERSION 3.1)
project(PackageTest C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(example test_package.c)
target_link_libraries(example ${CONAN_LIBS})
