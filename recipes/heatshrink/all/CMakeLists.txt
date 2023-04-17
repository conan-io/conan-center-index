cmake_minimum_required(VERSION 3.8)
project(heatshrink LANGUAGES C)

add_library(heatshrink
    ${HEATSHRINK_SRC_DIR}/heatshrink_decoder.c
    ${HEATSHRINK_SRC_DIR}/heatshrink_encoder.c
)
target_include_directories(heatshrink PUBLIC ${HEATSHRINK_SRC_DIR})
set_target_properties(heatshrink PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)
target_compile_features(heatshrink PRIVATE c_std_99)

include(GNUInstallDirs)
install(
    FILES
        ${HEATSHRINK_SRC_DIR}/heatshrink_common.h
        ${HEATSHRINK_SRC_DIR}/heatshrink_config.h
        ${HEATSHRINK_SRC_DIR}/heatshrink_decoder.h
        ${HEATSHRINK_SRC_DIR}/heatshrink_encoder.h
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

install(
    TARGETS heatshrink
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)
