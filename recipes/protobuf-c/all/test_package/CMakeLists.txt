cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

find_package(protobuf-c CONFIG REQUIRED)

protobuf_generate_c(GENERATED_PROTOBUF_SOURCES GENERATED_INCLUDE_DIR hero.proto)

add_executable(${PROJECT_NAME} test_package.c hero.proto ${GENERATED_PROTOBUF_SOURCES})
target_include_directories(${PROJECT_NAME} PRIVATE ${GENERATED_INCLUDE_DIR})
target_link_libraries(${PROJECT_NAME} protobuf-c::protobuf-c)
