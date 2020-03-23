cmake_minimum_required(VERSION 2.8.12)
project(PackageTest C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(example example.c)
target_link_libraries(example ${CONAN_LIBS})
set_target_properties(example PROPERTIES C_STANDARD 99)

