cmake_minimum_required(VERSION 2.8.12)
project(test_package)

find_package(libtool REQUIRED CONFIG)

include(GenerateExportHeader)

add_library(liba SHARED liba.c)
generate_export_header(liba)
target_include_directories(liba
    PUBLIC $<BUILD_INTERFACE:${PROJECT_BINARY_DIR}>
)

add_executable(${PROJECT_NAME} test_package.c)
include_directories(${LIBTOOL_INCLUDE_DIRS})
target_link_libraries(${PROJECT_NAME} PRIVATE libtool::libtool)

install(TARGETS test_package liba)
