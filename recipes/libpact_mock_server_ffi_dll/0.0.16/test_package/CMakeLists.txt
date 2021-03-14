cmake_minimum_required(VERSION 3.1)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

set( CMAKE_CXX_FLAGS " -pthread " )

add_executable(example example.cpp)
target_link_libraries(example ${CONAN_LIBS} dl)
include_directories(${CONAN_INCLUDE_DIRS})

enable_testing()
add_test(NAME example
         WORKING_DIRECTORY ${CMAKE_BINARY_DIR}/bin
         COMMAND example)
