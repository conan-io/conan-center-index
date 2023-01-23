cmake_minimum_required(VERSION 3.8)

project(test_package C)

find_package(Nanopb REQUIRED)

nanopb_generate_cpp(PROTO_SRC PROTO_HEADER simple.proto)

add_executable(${PROJECT_NAME} simple.c ${PROTO_SRC} ${PROTO_HEADER})

target_include_directories(${PROJECT_NAME} PRIVATE ${NANOPB_INCLUDE_DIRS} ${CMAKE_CURRENT_BINARY_DIR})

