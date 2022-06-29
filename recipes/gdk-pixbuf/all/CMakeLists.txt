cmake_minimum_required(VERSION 3.16)
project(compiler_rt_test)

try_compile(HAS_COMPILER_RT ${CMAKE_BINARY_DIR} ${CMAKE_SOURCE_DIR}/test.c OUTPUT_VARIABLE OUTPUT)

message(STATUS ${HAS_COMPILER_RT})
message(STATUS ${OUTPUT})

