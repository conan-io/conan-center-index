cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES CXX)

find_package(BISON REQUIRED)

set(BISON_VARS
    BISON_FOUND
    BISON_EXECUTABLE
    BISON_VERSION
)

foreach(BISON_VAR ${BISON_VARS})
    message("${BISON_VAR}: ${${BISON_VAR}}")
    if(NOT ${BISON_VAR})
        message(FATAL_ERROR "${BISON_VAR} NOT FOUND")
    endif()
endforeach()

bison_target(McParser mc_parser.yy "${CMAKE_CURRENT_BINARY_DIR}/mc_parser.cpp")
add_library(${PROJECT_NAME} STATIC ${BISON_McParser_OUTPUTS})
