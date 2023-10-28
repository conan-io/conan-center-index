cmake_minimum_required(VERSION 3.15)
project(detools LANGUAGES C)

find_package(heatshrink REQUIRED CONFIG)
find_package(LibLZMA REQUIRED CONFIG)

add_library(detools ${DETOOLS_SRC_DIR}/c/detools.c)
target_link_libraries(detools PRIVATE
    heatshrink::heatshrink
    LibLZMA::LibLZMA
)

include(GNUInstallDirs)

install(
    TARGETS detools
    DESTINATION ${CMAKE_INSTALL_LIBDIR}
)
install(
    FILES ${DETOOLS_SRC_DIR}/c/detools.h
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)
