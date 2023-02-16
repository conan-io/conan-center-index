cmake_minimum_required(VERSION 3.1)
project(test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(lexbor CONFIG REQUIRED)

add_executable(${PROJECT_NAME} test_package.c)

if(TARGET lexbor::lexbor_static)
    target_link_libraries(${PROJECT_NAME} lexbor::lexbor_static)
else()
    target_link_libraries(${PROJECT_NAME} lexbor::lexbor)
endif()
