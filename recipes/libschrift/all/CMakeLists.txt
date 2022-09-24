cmake_minimum_required(VERSION 3.8)
project(schrift LANGUAGES C)

include(GNUInstallDirs)

add_library(schrift ${LIBSCHRIFT_SRC_DIR}/schrift.c)
set_target_properties(schrift PROPERTIES
    PUBLIC_HEADER ${LIBSCHRIFT_SRC_DIR}/schrift.h
    WINDOWS_EXPORT_ALL_SYMBOLS ON
    C_EXTENSIONS OFF
    C_STANDARD 99
)

find_library(LIBM m)
target_link_libraries(schrift PRIVATE $<$<BOOL:${LIBM}>:${LIBM}>)

install(
    TARGETS schrift
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)
