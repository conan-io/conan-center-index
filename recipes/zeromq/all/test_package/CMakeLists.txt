cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES CXX)

option(WITH_LIBSODIUM "zeromq is built with libsodium")
option(WITH_NORM "zeromq is built with norm")

find_package(ZeroMQ REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
if(ZEROMQ_SHARED)
    target_link_libraries(${PROJECT_NAME} PRIVATE libzmq)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE libzmq-static)
endif()

if(WITH_LIBSODIUM)
    target_compile_definitions(${PROJECT_NAME} PRIVATE "WITH_LIBSODIUM")
endif()

if(WITH_NORM)
    target_compile_definitions(${PROJECT_NAME} PRIVATE "WITH_NORM")
endif()
