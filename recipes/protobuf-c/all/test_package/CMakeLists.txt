cmake_minimum_required(VERSION 3.1)
project(test_package)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup(TARGETS)

# include protobuf-c generator script and run generation
include(protobuf-gen-c.cmake)

protobuf_generate_c(GENERATED_PROTOBUF_SOURCES GENERATED_INCLUDE_DIR hero.proto)

add_executable(${PROJECT_NAME} test_package.c hero.proto ${GENERATED_PROTOBUF_SOURCES})
target_include_directories(${PROJECT_NAME} PRIVATE ${GENERATED_INCLUDE_DIR})
target_link_libraries(${PROJECT_NAME} protobuf-c::protobuf-c)

set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
