cmake_minimum_required(VERSION 3.12)
project(slz LANGUAGES C)

add_library(slz src/src/slz.c)
include_directories(src/src)
set_target_properties(slz PROPERTIES
    PUBLIC_HEADER src/src/slz.h
    WINDOWS_EXPORT_ALL_SYMBOLS ON
    C_STANDARD 11
    C_EXTENSIONS ON
)

include(GNUInstallDirs)
install(
    TARGETS slz
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)
