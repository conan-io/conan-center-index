cmake_minimum_required(VERSION 3.8)
project(slz LANGUAGES C)

include(conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)

include(GNUInstallDirs)

add_library(slz source_subfolder/src/slz.c)
include_directories(source_subfolder/src)
set_target_properties(slz PROPERTIES
    PUBLIC_HEADER source_subfolder/src/slz.h
    WINDOWS_EXPORT_ALL_SYMBOLS ON
    C_STANDARD 11
    C_EXTENSIONS ON
)

install(
    TARGETS slz
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)
