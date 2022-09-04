cmake_minimum_required(VERSION 3.4)
project(poly2tri LANGUAGES CXX)

include(GNUInstallDirs)

add_library(poly2tri
    ${POLY2TRI_SRC_DIR}/common/shapes.cc
    ${POLY2TRI_SRC_DIR}/sweep/advancing_front.cc
    ${POLY2TRI_SRC_DIR}/sweep/cdt.cc
    ${POLY2TRI_SRC_DIR}/sweep/sweep.cc
    ${POLY2TRI_SRC_DIR}/sweep/sweep_context.cc
)

if(MSVC AND BUILD_SHARED_LIBS)
    set_property(TARGET poly2tri PROPERTY WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()

install(
    TARGETS poly2tri
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

install(
    DIRECTORY ${POLY2TRI_SRC_DIR}
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    FILES_MATCHING PATTERN "*.h"
)
