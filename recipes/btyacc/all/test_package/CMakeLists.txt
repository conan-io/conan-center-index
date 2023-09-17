cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

enable_testing()

find_package(btyacc REQUIRED CONFIG)
if(NOT DEFINED BTYACC_EXECUTABLE)
    message(FATAL_ERROR "BTYACC_EXECUTABLE is not defined")
endif()

set(bin "${PROJECT_BINARY_DIR}")
add_custom_command(
    OUTPUT main.c
    COMMAND "${BTYACC_EXECUTABLE}" -b y "${PROJECT_SOURCE_DIR}/test.y"
    COMMAND "${CMAKE_COMMAND}" -E copy_if_different "${bin}/y.tab.c" "${bin}/main.c"
    COMMAND "${CMAKE_COMMAND}" -E remove "${bin}/y.tab.c"
    MAIN_DEPENDENCY test.y
    WORKING_DIRECTORY "${bin}"
    COMMENT "Generating main.c"
    VERBATIM
)

add_executable(test_package "${bin}/main.c")

add_test(
    NAME main
    COMMAND "${CMAKE_COMMAND}" -E echo "(())()(())" | test_package
)
