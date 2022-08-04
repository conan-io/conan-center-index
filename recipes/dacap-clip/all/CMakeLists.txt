cmake_minimum_required(VERSION 3.4)
project(cmake_wrapper)

set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
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
