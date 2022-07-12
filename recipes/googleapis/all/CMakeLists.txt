cmake_minimum_required(VERSION 3.8)
project(googleapis)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup(TARGETS)

find_package(Protobuf REQUIRED)


