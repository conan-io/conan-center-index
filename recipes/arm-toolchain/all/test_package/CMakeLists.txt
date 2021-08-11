cmake_minimum_required(VERSION 3.1)
project(test_package C)

option(ARM_64BIT "Is arm 64-bit?")
message("ARM_64BIT: ${ARM_64BIT}")

add_executable(${PROJECT_NAME} test_package.c)
target_compile_definitions(${PROJECT_NAME} PRIVATE ARM_64BIT=$<IF:$<BOOL:${ARM_64BIT}>,1,0>)
