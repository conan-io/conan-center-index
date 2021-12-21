cmake_minimum_required(VERSION 3.4)
project(heatshrink C)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup()

if (WIN32)
    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()

SET(SOURCE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder")

SET (CMAKE_C_STANDARD 99)
LIST(APPEND SRC_HEATSHRINK
    "${SOURCE_DIR}/heatshrink_decoder.c"
    "${SOURCE_DIR}/heatshrink_encoder.c")

include_directories(${SOURCE_DIR})

add_library(heatshrink ${SRC_HEATSHRINK})

install(
    FILES
        ${SOURCE_DIR}/heatshrink_common.h
        ${SOURCE_DIR}/heatshrink_config.h
        ${SOURCE_DIR}/heatshrink_decoder.h
        ${SOURCE_DIR}/heatshrink_encoder.h
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

install(TARGETS ${PROJECT_NAME}
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR})
