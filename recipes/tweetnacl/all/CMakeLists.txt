cmake_minimum_required(VERSION 3.12)
project(tweetnacl C)

add_library(tweetnacl tweetnacl.c)
set_target_properties(tweetnacl PROPERTIES PUBLIC_HEADER "tweetnacl.h")

include(GNUInstallDirs)
install(TARGETS tweetnacl
    PUBLIC_HEADER DESTINATION "${CMAKE_INSTALL_INCLUDEDIR}"
)
