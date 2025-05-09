cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(Thrift CONFIG REQUIRED QUIET)

# Find the thrift compiler
find_program(THRIFT_COMPILER NAMES thrift REQUIRED)

# Create a folder where the thrift compiler will generate the files
set(THRIFT_OUTPUT_DIR ${CMAKE_BINARY_DIR}/gen)
file(MAKE_DIRECTORY ${THRIFT_OUTPUT_DIR})

# We set the names of files generated here - not ideal but at least the build will fail if this was not generated
set(THRIFT_OUTPUT_FILES
    ${THRIFT_OUTPUT_DIR}/calc_constants.cpp
    ${THRIFT_OUTPUT_DIR}/calc_constants.h
    ${THRIFT_OUTPUT_DIR}/calc_types.cpp
    ${THRIFT_OUTPUT_DIR}/calc_types.h
    ${THRIFT_OUTPUT_DIR}/Calculator.cpp
    ${THRIFT_OUTPUT_DIR}/Calculator.h
)

# Tell cmake to generate the files if the expected files are missing or the thrift file changed
add_custom_command(
    COMMAND ${THRIFT_COMPILER}
        --gen cpp:include_prefix
        -r
        -out ${THRIFT_OUTPUT_DIR}
        -I ${CMAKE_CURRENT_SOURCE_DIR}
        ${CMAKE_CURRENT_SOURCE_DIR}/calc.thrift
    DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/calc.thrift
    OUTPUT  ${THRIFT_OUTPUT_FILES}
    COMMENT "Compiling Thrift IDL files")

# Our test executable compiles in the generated files
add_executable(${PROJECT_NAME}
    ${THRIFT_OUTPUT_FILES}
    test_package.cpp
)

# Allow us to #include <gen/<file>.h>
target_include_directories(${PROJECT_NAME}
    PUBLIC
        ${THRIFT_OUTPUT_DIR}/../
)

# Link to the thrift library
target_link_libraries(${PROJECT_NAME} PRIVATE thrift::thrift)
