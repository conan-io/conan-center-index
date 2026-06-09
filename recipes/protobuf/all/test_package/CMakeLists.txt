cmake_minimum_required(VERSION 3.15)

project(test_package LANGUAGES CXX)

find_package(protobuf CONFIG REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
if (EXISTS "${CMAKE_BINARY_DIR}/addressbook.pb.cc")
    target_sources(${PROJECT_NAME} PUBLIC ${CMAKE_BINARY_DIR}/addressbook.pb.cc)
endif()

if (protobuf_LITE)
    target_link_libraries(${PROJECT_NAME} PRIVATE protobuf::libprotobuf-lite)
    target_compile_definitions(${PROJECT_NAME} PRIVATE CONANTEST_PROTOBUF_LITE=1)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE protobuf::libprotobuf)
endif()

if(NOT TARGET protobuf::protoc)
    message(FATAL_ERROR "protoc executable should have been defined as part of find_package(protobuf)")
endif()

if(NOT COMMAND protobuf_generate)
    message(FATAL_ERROR "protobuf_generate should have been defined as part of find_package(protobuf)")
endif()
