cmake_minimum_required(VERSION 3.1.2)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

set(CMAKE_CXX_STANDARD 11)

add_executable(example example.cpp)
target_link_libraries(example ${CONAN_LIBS})

