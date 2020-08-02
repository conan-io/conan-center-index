# this is based off the echo_c++ example provided in brpc but simpler due to
# conan

cmake_minimum_required(VERSION 3.1.4)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

include(FindThreads)
include(FindProtobuf)
protobuf_generate_cpp(PROTO_SRC PROTO_HEADER echo.proto)
message("Generated: ${PROTO_SRC} ; ${PROTO_HEADER}")

# for PROTO_HEADER
include_directories(${CMAKE_CURRENT_BINARY_DIR})

set(CMAKE_CXX_STANDARD 11)

add_executable(test test.cpp ${PROTO_SRC} ${PROTO_HEADER})
target_link_libraries(test ${CONAN_LIBS})
