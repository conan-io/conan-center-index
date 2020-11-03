cmake_minimum_required(VERSION 3.1)
project(test_package)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup(TARGETS)

find_package(Protobuf CONFIG REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp addressbook.proto)
target_link_libraries(${PROJECT_NAME} protobuf::libprotobuf protobuf::libprotoc) # if protobuf is compiled as 'lite' this will fail
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
target_include_directories(${PROJECT_NAME} PRIVATE "${CMAKE_BINARY_DIR}")

protobuf_generate_cpp(PROTO_SRCS PROTO_HDRS TARGET ${PROJECT_NAME})
protobuf_generate(LANGUAGE cpp TARGET ${PROJECT_NAME} PROTOS addressbook.proto)

# # message(STATUS "PROTO_SRCS: ${PROTO_SRCS}")
# # message(STATUS "PROTO_HDRS: ${PROTO_HDRS}")
