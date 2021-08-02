cmake_minimum_required(VERSION 3.1)
project(PackageTest)

set(CMAKE_C_STANDARD 11)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(example example.c)
target_link_libraries(example PRIVATE ${CONAN_LIBS})
target_compile_options(example PRIVATE ${CONAN_COMPILE_DEFINITIONS_WASMTIME})
