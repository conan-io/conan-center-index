cmake_minimum_required(VERSION 3.15)
project(QR-Code-Generator)

include(src/files.cmake)

IF (COMPILE_AS_C)
    set(SRC ${CMAKE_SOURCE_DIR}/src/c/qrcodegen.c)
    set(CMAKE_C_STANDARD 99)
    set(LIBRARY_NAME qrcodegenc)
    set(HEADERS ${CMAKE_SOURCE_DIR}/src/c/qrcodegen.h)
    set(INCLUDE_DIR qrcodegenc)
ELSE ()
    set(INCLUDE_DIR qrcodegen)
ENDIF ()

add_library(${LIBRARY_NAME} ${SRC})

set_target_properties(${LIBRARY_NAME} PROPERTIES PUBLIC_HEADER "${HEADERS}")
install(TARGETS ${LIBRARY_NAME} RUNTIME LIBRARY ARCHIVE PUBLIC_HEADER DESTINATION include/${INCLUDE_DIR})
