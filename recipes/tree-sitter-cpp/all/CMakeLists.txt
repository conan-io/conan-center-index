cmake_minimum_required(VERSION 3.13)
project(tree-sitter-cpp C CXX)

find_package(tree-sitter REQUIRED CONFIG)
include(GenerateExportHeader)

# Check if the source files have .cc extension, which indicates C++
file(GLOB SOURCE_FILES "src/src/*.c" "src/src/*.cc")

# Set the linker language based on the file extension
if(SOURCE_FILES MATCHES ".*\\.cc$")
    set(LINKER_LANGUAGE stdc++)
else()
    set(LINKER_LANGUAGE c)
endif()

file(WRITE api.h [[
#pragma once
#include <tree_sitter/parser.h>
#include "tree_sitter_cpp_export.h"

#ifdef __cplusplus
extern "C" {
#endif

const TSLanguage *tree_sitter_cpp(void);

#ifdef __cplusplus
}
#endif
]])

add_library(${PROJECT_NAME} SHARED ${SOURCE_FILES})

target_link_libraries(${PROJECT_NAME}
    PRIVATE
    ${LINKER_LANGUAGE}
)

target_link_libraries(${PROJECT_NAME}
    PUBLIC
        tree-sitter::tree-sitter
)

target_include_directories(${PROJECT_NAME}
    PRIVATE
        $<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/src/lib/include>
        $<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/src/src>
)

set_target_properties(${PROJECT_NAME}
    PROPERTIES
        C_STANDARD 99
        PUBLIC_HEADER "api.h;${CMAKE_CURRENT_BINARY_DIR}/tree_sitter_cpp_export.h"
)

generate_export_header(${PROJECT_NAME}
    BASE_NAME TREE_SITTER_CPP
    EXPORT_FILE_NAME "tree_sitter_cpp_export.h"
)

include(GNUInstallDirs)
install(TARGETS ${PROJECT_NAME}
    ARCHIVE DESTINATION "${CMAKE_INSTALL_LIBDIR}"
    LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}"
    RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}"
    PUBLIC_HEADER DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}/tree_sitter_cpp"
)
