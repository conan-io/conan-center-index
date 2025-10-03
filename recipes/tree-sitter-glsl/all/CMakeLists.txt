cmake_minimum_required(VERSION 3.15)
project(tree-sitter-glsl
        DESCRIPTION "GLSL grammar for tree-sitter"
        HOMEPAGE_URL "https://github.com/tree-sitter-grammars/tree-sitter-glsl"
        LANGUAGES C)

find_package(tree-sitter REQUIRED CONFIG)

add_library(${PROJECT_NAME}
    "${CMAKE_CURRENT_SOURCE_DIR}/src/src/parser.c"
)
target_link_libraries(${PROJECT_NAME}
    PUBLIC
        tree-sitter::tree-sitter
)
target_include_directories(${PROJECT_NAME}
    PRIVATE
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src>
)
set_target_properties(${PROJECT_NAME}
    PROPERTIES
        C_STANDARD 99
        PUBLIC_HEADER "${CMAKE_CURRENT_SOURCE_DIR}/src/bindings/c/tree-sitter-glsl.h"
)

include(GNUInstallDirs)
install(TARGETS ${PROJECT_NAME}
    ARCHIVE DESTINATION "${CMAKE_INSTALL_LIBDIR}"
    LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}"
    RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}"
    PUBLIC_HEADER DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}"
)
