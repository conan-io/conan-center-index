cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper)

add_subdirectory(source_subfolder)

include(GNUInstallDirs)

install(
    TARGETS clip
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

install(
    FILES source_subfolder/clip.h
    DESTINATION  ${CMAKE_INSTALL_INCLUDEDIR}
)
