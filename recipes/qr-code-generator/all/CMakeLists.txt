cmake_minimum_required(VERSION 3.15)
project(QR-Code-Generator)


set(SRC_C ${CMAKE_SOURCE_DIR}/src/c/qrcodegen.c)
set(LIBRARY_NAME_C qrcodegenc)
set(HEADERS_C ${CMAKE_SOURCE_DIR}/src/c/qrcodegen.h)

add_library(${LIBRARY_NAME_C} ${SRC_C})
set_target_properties(${LIBRARY_NAME_C} PROPERTIES PUBLIC_HEADER "${HEADERS_C}")
install(TARGETS ${LIBRARY_NAME_C} RUNTIME LIBRARY ARCHIVE PUBLIC_HEADER DESTINATION include/qrcodegenc)

include(src/files.cmake)
add_library(${LIBRARY_NAME} ${SRC})
set_target_properties(${LIBRARY_NAME} PROPERTIES PUBLIC_HEADER "${HEADERS}")
install(TARGETS ${LIBRARY_NAME} RUNTIME LIBRARY ARCHIVE PUBLIC_HEADER DESTINATION include/qrcodegen)
