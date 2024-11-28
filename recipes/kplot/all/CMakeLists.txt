cmake_minimum_required(VERSION 3.15)
project(kplot LANGUAGES C)

find_package(cairo REQUIRED CONFIG)

set(kplot_src
    colours.c
    array.c
    border.c
    bucket.c
    buffer.c
    draw.c
    grid.c
    hist.c
    label.c
    kdata.c
    kplot.c
    margin.c
    mean.c
    plotctx.c
    reallocarray.c
    stddev.c
    tic.c
    vector.c
)

set(kplot_inc
    compat.h
    extern.h
    kplot.h
)

try_run(HAVE_reallocarray COMPIE_reallocarray ${CMAKE_BINARY_DIR} "${CMAKE_SOURCE_DIR}/test-reallocarray.c")
file(READ compat.pre.h COMPAT_CONTENTS)
file(WRITE compat.h "${COMPAT_CONTENTS}")
if (COMPIE_reallocarray AND NOT HAVE_reallocarray)
    file(APPEND compat.h "#define  HAVE_REALLOCARRAY")
endif()
file(READ compat.post.h COMPAT_CONTENTS)
file(APPEND compat.h "${COMPAT_CONTENTS}")

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
