cmake_minimum_required(VERSION 2.8.12)
project(test_package)

find_package(libtool REQUIRED CONFIG)

include(GenerateExportHeader)

add_library(liba MODULE liba.c)
generate_export_header(liba)
target_include_directories(liba
    PUBLIC $<BUILD_INTERFACE:${PROJECT_BINARY_DIR}>
)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE libtool::libtool)

add_library(static_lib STATIC
    static_lib.c
)

install(TARGETS static_lib
        LIBRARY
            DESTINATION lib
            COMPONENT static_lib
        ARCHIVE
            DESTINATION lib
            COMPONENT static_lib)
