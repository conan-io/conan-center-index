cmake_minimum_required(VERSION 3.0)
project(tree-sitter-c C)

find_package(tree-sitter REQUIRED CONFIG)
include(GenerateExportHeader)

file(WRITE api.h [[
#pragma once
#include <tree_sitter/parser.h>
#include "tree_sitter_c_export.h"

#ifdef __cplusplus
extern "C" {
#endif

const TSLanguage *tree_sitter_c(void);

#ifdef __cplusplus
}
#endif
]])

add_library(${PROJECT_NAME}
    src/parser.c
)
target_link_libraries(${PROJECT_NAME}
    PUBLIC
        tree-sitter::tree-sitter
)
target_include_directories(${PROJECT_NAME}
    PRIVATE
        $<BUILD_INTERFACE:${TREE_SITTER_C_SRC_DIR}/src>
)
set_target_properties(${PROJECT_NAME}
    PROPERTIES
        C_STANDARD 99
        PUBLIC_HEADER "api.h;${CMAKE_CURRENT_BINARY_DIR}/tree_sitter_c_export.h"
)
generate_export_header(${PROJECT_NAME}
    BASE_NAME TREE_SITTER_C
    EXPORT_FILE_NAME "tree_sitter_c_export.h"
)

include(GNUInstallDirs)
install(TARGETS ${PROJECT_NAME}
    ARCHIVE DESTINATION "${CMAKE_INSTALL_LIBDIR}"
    LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}"
    RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}"
    PUBLIC_HEADER DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}/tree_sitter_c"
)
