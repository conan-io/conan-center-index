cmake_minimum_required(VERSION 3.4)
project(tree-sitter LANGUAGES C)

# Use cmake script instead of Makefile to support MSVC + follow fPIC option

file(GLOB SOURCES ${TREE_SITTER_SRC_DIR}/lib/src/*.c)
list(REMOVE_ITEM SOURCES ${TREE_SITTER_SRC_DIR}/lib/src/lib.c)

file(GLOB HEADERS ${TREE_SITTER_SRC_DIR}/lib/include/tree_sitter/*.h)

add_library(${PROJECT_NAME} ${SOURCES})
target_include_directories(${PROJECT_NAME}
    PRIVATE
        $<BUILD_INTERFACE:${TREE_SITTER_SRC_DIR}/lib/include>
        $<BUILD_INTERFACE:${TREE_SITTER_SRC_DIR}/lib/src>
)
set_target_properties(${PROJECT_NAME}
    PROPERTIES
        PUBLIC_HEADER "${HEADERS}"
        WINDOWS_EXPORT_ALL_SYMBOLS ON
)

if(TREE_SITTER_VERSION VERSION_LESS "0.21.0")
    target_compile_features(${PROJECT_NAME} PRIVATE c_std_99)
else()
    target_compile_features(${PROJECT_NAME} PRIVATE c_std_11)
endif()

include(GNUInstallDirs)
install(TARGETS ${PROJECT_NAME}
    ARCHIVE DESTINATION "${CMAKE_INSTALL_LIBDIR}"
    LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}"
    RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}"
    PUBLIC_HEADER DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}/tree_sitter"
)
