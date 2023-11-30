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

# _USE_MATH_DEFINES is defined in utils.h where M_PI is used, but it can break because math.h or cmath
# may have already been included indirectly by other headers included by sweep.cc before inclusion of utils.h
# Therefore we ensure that _USE_MATH_DEFINES is defined before any inclusion of headers.
target_compile_definitions(poly2tri PRIVATE _USE_MATH_DEFINES)

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
