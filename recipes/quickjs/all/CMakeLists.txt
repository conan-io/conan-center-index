cmake_minimum_required(VERSION 3.4)
project(quickjs C)

option(USE_BIGNUM "Use bignum" ON)
option(DUMP_LEAKS "dump leaks" OFF)

file(STRINGS ${QUICKJS_SRC_DIR}/VERSION version)
set(cdef CONFIG_VERSION="${version}" _GNU_SOURCE)

set(QUICKJS_SRC
    ${QUICKJS_SRC_DIR}/quickjs.c
    ${QUICKJS_SRC_DIR}/libbf.c
    ${QUICKJS_SRC_DIR}/libregexp.c
    ${QUICKJS_SRC_DIR}/libunicode.c
    ${QUICKJS_SRC_DIR}/cutils.c
    ${QUICKJS_SRC_DIR}/quickjs-libc.c
)

set(QUICKJS_INC
    ${QUICKJS_SRC_DIR}/cutils.h
    ${QUICKJS_SRC_DIR}/libregexp-opcode.h
    ${QUICKJS_SRC_DIR}/libregexp.h
    ${QUICKJS_SRC_DIR}/libunicode-table.h
    ${QUICKJS_SRC_DIR}/libunicode.h
    ${QUICKJS_SRC_DIR}/list.h
    ${QUICKJS_SRC_DIR}/quickjs-atom.h
    ${QUICKJS_SRC_DIR}/quickjs-libc.h
    ${QUICKJS_SRC_DIR}/quickjs-opcode.h
    ${QUICKJS_SRC_DIR}/quickjs.h
    ${QUICKJS_SRC_DIR}/unicode_gen_def.h
)

if(USE_BIGNUM)
    list(APPEND QUICKJS_SRC ${QUICKJS_SRC_DIR}/libbf.c)
    list(APPEND QUICKJS_INC ${QUICKJS_SRC_DIR}/libbf.h)
endif()

add_library(quickjs ${QUICKJS_SRC})
target_include_directories(quickjs PRIVATE ${QUICKJS_SRC_DIR})
set_target_properties(quickjs PROPERTIES
    PUBLIC_HEADER "${QUICKJS_INC}"
    WINDOWS_EXPORT_ALL_SYMBOLS ON
)

if(USE_BIGNUM)
    target_compile_definitions(quickjs PRIVATE CONFIG_BIGNUM)
endif()

find_library(LIBM m)
target_link_libraries(quickjs PRIVATE $<$<BOOL:${LIBM}>:${LIBM}>)

if(DUMP_LEAKS)
    target_compile_definitions(quickjs PRIVATE ${cdef} DUMP_LEAKS)
else()
    target_compile_definitions(quickjs PRIVATE ${cdef})
endif()

include(GNUInstallDirs)

install(
    TARGETS quickjs
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/quickjs
)
