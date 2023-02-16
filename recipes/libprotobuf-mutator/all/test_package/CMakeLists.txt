cmake_minimum_required(VERSION 3.1)
project(test_package CXX)


include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)
find_package(libprotobuf-mutator REQUIRED CONFIG)


protobuf_generate_cpp(
    MSG_PROTO_SRCS
    MSG_PROTO_HDRS
    msg.proto
)


add_executable(${PROJECT_NAME} ${MSG_PROTO_SRCS} test_package.cpp)
target_include_directories(${PROJECT_NAME} PRIVATE ${CMAKE_CURRENT_BINARY_DIR})
target_link_libraries(${PROJECT_NAME} libprotobuf-mutator::libprotobuf-mutator)
