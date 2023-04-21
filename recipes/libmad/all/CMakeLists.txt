cmake_minimum_required(VERSION 3.15)
project(libmad LANGUAGES C)

add_library(libmad
    ${LIBMAD_SRC_DIR}/bit.c
    ${LIBMAD_SRC_DIR}/decoder.c
    ${LIBMAD_SRC_DIR}/fixed.c
    ${LIBMAD_SRC_DIR}/frame.c
    ${LIBMAD_SRC_DIR}/huffman.c
    ${LIBMAD_SRC_DIR}/layer12.c
    ${LIBMAD_SRC_DIR}/layer3.c
    ${LIBMAD_SRC_DIR}/stream.c
    ${LIBMAD_SRC_DIR}/synth.c
    ${LIBMAD_SRC_DIR}/timer.c
    ${LIBMAD_SRC_DIR}/version.c
    ${LIBMAD_SRC_DIR}/huffman.c
)

target_include_directories(libmad PUBLIC ${LIBMAD_SRC_DIR}/msvc++)
target_compile_definitions(libmad PRIVATE FPM_DEFAULT ASO_ZEROCHECK HAVE_CONFIG_H)
set_target_properties(libmad PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)

include(GNUInstallDirs)
install(FILES ${LIBMAD_SRC_DIR}/msvc++/mad.h DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
install(
    TARGETS libmad
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_LIBDIR}
)
