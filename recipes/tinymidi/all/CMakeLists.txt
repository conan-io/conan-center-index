cmake_minimum_required(VERSION 3.15)
project(tinymidi LANGUAGES C)

add_library(tinymidi ${TINYMIDI_SRC_DIR}/rawmidi.c)

include(GNUInstallDirs)
install(FILES ${TINYMIDI_SRC_DIR}/include/rawmidi.h DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
install(
    TARGETS tinymidi
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_LIBDIR}
)
