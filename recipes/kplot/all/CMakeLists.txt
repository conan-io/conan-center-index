cmake_minimum_required(VERSION 3.8)
project(kplot LANGUAGES C)

find_package(cairo REQUIRED CONFIG)

set(kplot_src
    ${KPLOT_SRC_DIR}/colours.c
    ${KPLOT_SRC_DIR}/array.c
    ${KPLOT_SRC_DIR}/border.c
    ${KPLOT_SRC_DIR}/bucket.c
    ${KPLOT_SRC_DIR}/buffer.c
    ${KPLOT_SRC_DIR}/draw.c
    ${KPLOT_SRC_DIR}/grid.c
    ${KPLOT_SRC_DIR}/hist.c
    ${KPLOT_SRC_DIR}/label.c
    ${KPLOT_SRC_DIR}/kdata.c
    ${KPLOT_SRC_DIR}/kplot.c
    ${KPLOT_SRC_DIR}/margin.c
    ${KPLOT_SRC_DIR}/mean.c
    ${KPLOT_SRC_DIR}/plotctx.c
    ${KPLOT_SRC_DIR}/reallocarray.c
    ${KPLOT_SRC_DIR}/stddev.c
    ${KPLOT_SRC_DIR}/tic.c
    ${KPLOT_SRC_DIR}/vector.c
)

set(kplot_inc
    ${KPLOT_SRC_DIR}/compat.h
    ${KPLOT_SRC_DIR}/extern.h
    ${KPLOT_SRC_DIR}/kplot.h
)

include_directories(KPLOT_SRC_DIR)

try_run(HAVE_reallocarray COMPIE_reallocarray ${CMAKE_BINARY_DIR} ${KPLOT_SRC_DIR}/test-reallocarray.c)

file(READ "${KPLOT_SRC_DIR}/compat.pre.h" COMPAT_CONTENTS)
file(WRITE "${KPLOT_SRC_DIR}/compat.h" "${COMPAT_CONTENTS}")
if (${COMPIE_reallocarray} AND NOT ${HAVE_reallocarray})
    file(APPEND "${KPLOT_SRC_DIR}/compat.h" "#define  HAVE_REALLOCARRAY")
endif()
file(READ "${KPLOT_SRC_DIR}/compat.post.h" COMPAT_CONTENTS)
file(APPEND "${KPLOT_SRC_DIR}/compat.h" "${COMPAT_CONTENTS}")

add_library(kplot ${kplot_src})

target_compile_features(kplot PRIVATE c_std_99)
set_target_properties(kplot PROPERTIES
    PUBLIC_HEADER "${kplot_inc}"
    WINDOWS_EXPORT_ALL_SYMBOLS ON
    C_EXTENSIONS OFF
)
target_compile_features(kplot PRIVATE c_std_99)
target_link_libraries(kplot PRIVATE cairo::cairo)

include(GNUInstallDirs)

install(
    TARGETS kplot
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)
