cmake_minimum_required(VERSION 3.13)

project(tree-sitter-glsl
        DESCRIPTION "GLSL grammar for tree-sitter"
        HOMEPAGE_URL "https://github.com/tree-sitter-grammars/tree-sitter-glsl"
        LANGUAGES C)

option(BUILD_SHARED_LIBS "Build using shared libraries" ON)
option(TREE_SITTER_REUSE_ALLOCATOR "Reuse the library allocator" OFF)

add_library(tree-sitter-glsl src/parser.c)
if(EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/src/scanner.c)
  target_sources(tree-sitter-glsl PRIVATE src/scanner.c)
endif()
target_include_directories(tree-sitter-glsl PRIVATE src)

target_compile_definitions(tree-sitter-glsl PRIVATE
                           $<$<BOOL:${TREE_SITTER_REUSE_ALLOCATOR}>:TREE_SITTER_REUSE_ALLOCATOR>
                           $<$<CONFIG:Debug>:TREE_SITTER_DEBUG>)

configure_file(bindings/c/tree-sitter-glsl.pc.in
               "${CMAKE_CURRENT_BINARY_DIR}/tree-sitter-glsl.pc" @ONLY)

include(GNUInstallDirs)

install(FILES bindings/c/tree-sitter-glsl.h
        DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}/tree_sitter")
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/tree-sitter-glsl.pc"
        DESTINATION "${CMAKE_INSTALL_DATAROOTDIR}/pkgconfig")
install(TARGETS tree-sitter-glsl
        LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}")

