cmake_minimum_required(VERSION 3.15)
project(PackageTest C)

find_package(SWIG REQUIRED CONFIG)
include(UseSWIG)

find_package(Python REQUIRED COMPONENTS Interpreter Development)

swig_add_library(${PROJECT_NAME}
    LANGUAGE python
    SOURCES test.i test_package.c
    OUTPUT_DIR ${CMAKE_BINARY_DIR}
)
target_link_libraries(${PROJECT_NAME} PRIVATE Python::Python)

# Note: this does not copy the generated *.py file
install(TARGETS ${PROJECT_NAME}
    LIBRARY DESTINATION ${CMAKE_BINARY_DIR}
    RUNTIME DESTINATION ${CMAKE_BINARY_DIR}
)
