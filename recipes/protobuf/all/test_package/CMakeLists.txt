cmake_minimum_required(VERSION 3.15)

project(test_package LANGUAGES CXX)

find_package(protobuf CONFIG REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp addressbook.proto)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
target_include_directories(${PROJECT_NAME} PRIVATE "${CMAKE_CURRENT_BINARY_DIR}")
if (protobuf_LITE)
    target_link_libraries(${PROJECT_NAME} PRIVATE protobuf::libprotobuf-lite)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE protobuf::libprotobuf)
endif()

if(TARGET protobuf::libprotoc)
    target_link_libraries(${PROJECT_NAME} PRIVATE protobuf::libprotoc)
endif()

if(TARGET protobuf::libutf8_validity)
    target_link_libraries(${PROJECT_NAME} PRIVATE protobuf::libutf8_validity)
endif()

protobuf_generate_cpp(PROTO_SRCS PROTO_HDRS TARGET ${PROJECT_NAME})
protobuf_generate(LANGUAGE cpp TARGET ${PROJECT_NAME} PROTOS addressbook.proto)
