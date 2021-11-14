cmake_minimum_required(VERSION 3.1)
project(heatshrink C)

SET(SOURCE_DIR ${CMAKE_SOURCE_DIR}/${SOURCE_SUBDIR} )

SET (CMAKE_C_STANDARD 99)
FILE(GLOB SRC_HEATSHRINK "${SOURCE_DIR}/heatshrink*.c")

include_directories(${SOURCE_DIR})

add_library(heatshrink ${SRC_HEATSHRINK})

install(
    FILES
        ${SOURCE_DIR}/heatshrink_common.h
        ${SOURCE_DIR}/heatshrink_config.h
        ${SOURCE_DIR}/heatshrink_decoder.h
        ${SOURCE_DIR}/heatshrink_encoder.h
    DESTINATION ${CMAKE_INSTALL_PREFIX}/include
)

INSTALL (TARGETS heatshrink
    LIBRARY DESTINATION ${CMAKE_INSTALL_PREFIX}/lib
)
