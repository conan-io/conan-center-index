cmake_minimum_required(VERSION 2.8.12)
project(test_package)

find_package(libtool REQUIRED)
include(GenerateExportHeader)

add_library(liba SHARED liba.c)
generate_export_header(liba)
target_include_directories(liba
    PUBLIC $<BUILD_INTERFACE:${PROJECT_BINARY_DIR}>
)
set_property(TARGET liba PROPERTY PREFIX "")

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE libtool::libtool)
target_include_directories(test_package
    PUBLIC "$<BUILD_INTERFACE:${PROJECT_BINARY_DIR}>"
)
