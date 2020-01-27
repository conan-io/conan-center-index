cmake_minimum_required(VERSION 2.8.12)
project(test_package)

set(CMAKE_VERBOSE_MAKEFILE TRUE)

option(WITH_LIBSODIUM "zeromq is built with libsodium")

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup()

find_package(ZeroMQ REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} ZeroMQ::ZeroMQ)

if(WITH_LIBSODIUM)
  target_compile_definitions(${PROJECT_NAME} PRIVATE "WITH_LIBSODIUM")
endif()
