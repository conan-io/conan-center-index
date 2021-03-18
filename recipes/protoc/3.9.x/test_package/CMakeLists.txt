cmake_minimum_required(VERSION 2.8.12)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

set(CMAKE_VERBOSE_MAKEFILE ON)

find_package(protoc CONFIG REQUIRED)

message(STATUS "Using Protocol Buffers ${protobuf_VERSION}")

if(protobuf_MODULE_COMPATIBLE)
    PROTOBUF_GENERATE_CPP(PROTO_SRCS PROTO_HDRS addressbook.proto)
    message(STATUS "PROTO_SRCS: ${PROTO_SRCS}")
    message(STATUS "PROTO_HDRS: ${PROTO_HDRS}")
endif(protobuf_MODULE_COMPATIBLE)
