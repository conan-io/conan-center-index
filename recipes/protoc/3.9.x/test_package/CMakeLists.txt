cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(Protobuf REQUIRED)
find_package(protoc REQUIRED)

if (NOT protobuf_MODULE_COMPATIBLE)
    message(FATAL_ERROR "protobuf_MODULE_COMPATIBLE is mandatory")
endif()

add_executable(${PROJECT_NAME} test_package.cpp addressbook.proto)
protobuf_generate_cpp(PROTO_SRCS PROTO_HDRS TARGET ${PROJECT_NAME})
message(STATUS "PROTO_SRCS: ${PROTO_SRCS}")
message(STATUS "PROTO_HDRS: ${PROTO_HDRS}")
target_include_directories(${PROJECT_NAME} PRIVATE ${PROJECT_BINARY_DIR})
target_link_libraries(${PROJECT_NAME} PRIVATE Protobuf::Protobuf)
