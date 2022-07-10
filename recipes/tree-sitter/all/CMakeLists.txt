cmake_minimum_required(VERSION 3.4)
project(tree-sitter C)

include(conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

# Use cmake script instead of Makefile to support MSVC + follow fPIC option

file(GLOB SOURCES RELATIVE "${PROJECT_SOURCE_DIR}" source_subfolder/lib/src/*.c)
list(REMOVE_ITEM SOURCES source_subfolder/lib/src/lib.c)

file(GLOB HEADERS source_subfolder/lib/include/tree_sitter/*.h)

add_library(${PROJECT_NAME} ${SOURCES})
target_include_directories(${PROJECT_NAME}
    PRIVATE
        $<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/source_subfolder/lib/include>
        $<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/source_subfolder/lib/src>
)
set_target_properties(${PROJECT_NAME}
    PROPERTIES
        C_STANDARD 99
        PUBLIC_HEADER "${HEADERS}"
        WINDOWS_EXPORT_ALL_SYMBOLS ON
)

include(GNUInstallDirs)
install(TARGETS ${PROJECT_NAME}
    ARCHIVE DESTINATION "${CMAKE_INSTALL_LIBDIR}"
    LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}"
    RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}"
    PUBLIC_HEADER DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}/tree_sitter"
)
