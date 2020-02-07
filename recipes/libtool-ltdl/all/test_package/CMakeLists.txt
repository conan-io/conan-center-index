cmake_minimum_required(VERSION 2.8.12)
project(test_package)

set(CMAKE_VERBOSE_MAKEFILE TRUE)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

include(GenerateExportHeader)

add_library(liba SHARED liba.c)
generate_export_header(liba)
target_include_directories(liba
    PUBLIC $<BUILD_INTERFACE:${PROJECT_BINARY_DIR}>
)
set_target_properties(liba
    PROPERTIES PREFIX "")

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
target_include_directories(test_package
    PUBLIC $<BUILD_INTERFACE:${PROJECT_BINARY_DIR}>
)
