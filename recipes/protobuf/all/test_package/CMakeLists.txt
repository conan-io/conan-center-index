cmake_minimum_required(VERSION 2.8.12)
project(test_package)

include("${CMAKE_BINARY_DIR}/../conanbuildinfo.cmake")
conan_basic_setup()

option(PROTOC_AVAILABLE "protobuf is available")

add_executable(${PROJECT_NAME} test_package.cpp addressbook.proto)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
target_include_directories(${PROJECT_NAME} PRIVATE "${CMAKE_BINARY_DIR}")

if(PROTOC_AVAILABLE)
    find_package(Protobuf REQUIRED)
    protobuf_generate_cpp(PROTO_SRCS PROTO_HDRS TARGET ${PROJECT_NAME})

    message(STATUS "PROTO_SRCS: ${PROTO_SRCS}")
    message(STATUS "PROTO_HDRS: ${PROTO_HDRS}")
else()
    target_sources(${PROJECT_NAME} PRIVATE "${CMAKE_BINARY_DIR}/addressbook.pb.cc" "${CMAKE_BINARY_DIR}/addressbook.pb.h")
endif()
