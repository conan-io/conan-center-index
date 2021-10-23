cmake_minimum_required(VERSION 2.8.12)
project(tweetnacl C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

include(GNUInstallDirs)

add_library(tweetnacl tweetnacl.c)
set_target_properties(tweetnacl PROPERTIES PUBLIC_HEADER "tweetnacl.h")

install(TARGETS tweetnacl
    ARCHIVE DESTINATION "${CMAKE_INSTALL_LIBDIR}"
    LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}"
    RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}"
    PUBLIC_HEADER DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}"
)
