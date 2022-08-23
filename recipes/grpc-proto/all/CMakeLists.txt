cmake_minimum_required(VERSION 3.4)

project(grpc-proto)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup(TARGETS)

find_package(Protobuf REQUIRED CONFIG)
find_package(googleapis REQUIRED CONFIG)

set(IMPORT_DIRS ${CMAKE_SOURCE_DIR} ${GOOGLEAPIS_PROTO_DIRS})

set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
