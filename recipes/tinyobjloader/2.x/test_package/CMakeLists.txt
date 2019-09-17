cmake_minimum_required(VERSION 2.8.11)
project(test_package CXX)

set(CMAKE_VERBOSE_MAKEFILE TRUE)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

configure_file(cube.obj cube.obj COPYONLY)
configure_file(cube.mtl cube.mtl COPYONLY)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})