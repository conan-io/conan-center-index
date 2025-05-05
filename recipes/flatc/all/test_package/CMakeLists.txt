cmake_minimum_required(VERSION 3.1)
project(test_package)


include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup()

find_package(flatc REQUIRED)

build_flatbuffers("test_package.fbs" "" flatbuffers "" "${CMAKE_CURRENT_BINARY_DIR}" "" "")

add_executable(${PROJECT_NAME} ${CMAKE_CURRENT_BINARY_DIR}/test_package_generated.h test_package.cpp)
