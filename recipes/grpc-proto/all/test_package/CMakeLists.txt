cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(protobuf REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE protobuf::protobuf)
target_include_directories(${PROJECT_NAME} PRIVATE ${CMAKE_CURRENT_BINARY_DIR})


message("GRPC_PROTO_RES_DIR -- ${GRPC_PROTO_RES_DIR}")
protobuf_generate(
    LANGUAGE cpp 
    TARGET ${PROJECT_NAME} 
    PROTOS ${GRPC_PROTO_RES_DIR}/grpc/health/v1/health.proto
    IMPORT_DIRS ${GRPC_PROTO_RES_DIR})
