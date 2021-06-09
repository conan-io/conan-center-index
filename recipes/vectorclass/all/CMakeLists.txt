cmake_minimum_required(VERSION 3.0 FATAL_ERROR)

project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

set(SOURCES
    ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/instrset_detect.cpp)

set(HEADERS
    ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/instrset.h
    ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/vector_convert.h
    ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/vectorclass.h
    ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/vectorf128.h
    ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/vectorf256.h
    ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/vectorf256e.h
    ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/vectorf512.h
    ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/vectorf512e.h
    ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/vectori128.h
    ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/vectori256.h
    ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/vectori256e.h
    ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/vectori512.h
    ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/vectori512e.h
    ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/vectori512s.h
    ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/vectori512se.h
    ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/vectormath_common.h
    ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/vectormath_exp.h
    ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/vectormath_hyp.h
    ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/vectormath_lib.h
    ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/vectormath_trig.h)

add_library(vectorclass STATIC ${SOURCES} ${HEADERS})

set_target_properties(vectorclass PROPERTIES PUBLIC_HEADER "${HEADERS}")

include(GNUInstallDirs)
install(TARGETS vectorclass
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
