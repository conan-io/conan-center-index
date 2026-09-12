cmake_minimum_required(VERSION 3.15)
project(ufbx C)

set(UFBX_SOURCES src/ufbx.c)
set(UFBX_HEADERS src/ufbx.h)
add_library(ufbx ${UFBX_SOURCES} ${UFBX_HEADERS})


set_target_properties(ufbx PROPERTIES
    PUBLIC_HEADER "${UFBX_HEADERS}"
    OUTPUT_NAME "ufbx"
    # As a C library, this is not too worriesome
    WINDOWS_EXPORT_ALL_SYMBOLS ON
)

include(GNUInstallDirs)

install(TARGETS ufbx)
