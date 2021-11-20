cmake_minimum_required(VERSION 3.0)
project(tree-sitter-c C)

include(conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(tree-sitter REQUIRED CONFIG)

file(WRITE api.h [[
#pragma once
#include <tree_sitter/parser.h>

extern const TSLanguage *tree_sitter_c(void);
]])

add_library(${PROJECT_NAME}
    source_subfolder/src/parser.c
)
target_link_libraries(${PROJECT_NAME}
    PUBLIC
        tree-sitter::tree-sitter
)
target_include_directories(${PROJECT_NAME}
    PRIVATE
        $<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/source_subfolder/lib/include>
        $<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/source_subfolder/src>
)
set_target_properties(${PROJECT_NAME}
    PROPERTIES
        C_STANDARD 99
        PUBLIC_HEADER "api.h"
)

include(GNUInstallDirs)
install(TARGETS ${PROJECT_NAME}
    ARCHIVE DESTINATION "${CMAKE_INSTALL_LIBDIR}"
    LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}"
    RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}"
    PUBLIC_HEADER DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}/tree_sitter_c"
)
