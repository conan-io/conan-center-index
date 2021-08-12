cmake_minimum_required(VERSION 3.1)
project(test_package C)

option(ARM_64BIT "Is arm 64-bit?")
message("ARM_64BIT: ${ARM_64BIT}")

if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
    add_executable(${PROJECT_NAME} test_package.c)
else()
    add_library(${PROJECT_NAME} STATIC test_package.c)
endif()
target_compile_definitions(${PROJECT_NAME} PRIVATE ARM_64BIT=$<IF:$<BOOL:${ARM_64BIT}>,1,0>)
