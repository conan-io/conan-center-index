cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

find_package(protobuf-c CONFIG REQUIRED)

protobuf_generate_c(TEST_PROTO_SRCS TEST_PROTO_HDRS hero.proto)

add_executable(${PROJECT_NAME} test_package.c hero.proto ${TEST_PROTO_SRCS} ${TEST_PROTO_HDRS})
target_include_directories(${PROJECT_NAME} PRIVATE ${CMAKE_CURRENT_BINARY_DIR})
target_link_libraries(${PROJECT_NAME} protobuf-c::protobuf-c)
