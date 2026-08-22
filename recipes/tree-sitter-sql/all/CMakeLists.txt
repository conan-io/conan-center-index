cmake_minimum_required(VERSION 3.15)
project(tree-sitter-sql LANGUAGES C)

find_package(tree-sitter REQUIRED CONFIG)

add_library(${PROJECT_NAME}
    ${TREE_SITTER_SQL_SRC_DIR}/src/scanner.c
    ${TREE_SITTER_SQL_SRC_DIR}/src/parser.c
)
target_link_libraries(${PROJECT_NAME}
    PUBLIC
        tree-sitter::tree-sitter
)
target_include_directories(${PROJECT_NAME}
    PRIVATE
        $<BUILD_INTERFACE:${TREE_SITTER_SQL_SRC_DIR}/src>
)
set_target_properties(${PROJECT_NAME}
    PROPERTIES
        C_STANDARD 99
        PUBLIC_HEADER "${TREE_SITTER_SQL_SRC_DIR}/bindings/c/tree-sitter-sql.h"
)

include(GNUInstallDirs)
install(TARGETS ${PROJECT_NAME}
    ARCHIVE DESTINATION "${CMAKE_INSTALL_LIBDIR}"
    LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}"
    RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}"
    PUBLIC_HEADER DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}"
)
