cmake_minimum_required(VERSION 3.1)
project(LibbpfTest C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(example example.c)
target_link_libraries(example ${CONAN_LIBS})
