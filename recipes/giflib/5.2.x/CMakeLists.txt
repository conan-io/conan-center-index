cmake_minimum_required(VERSION 3.1)
project(gif LANGUAGES C)

include(GNUInstallDirs)

add_library(gif
    "${GIFLIB_SRC_DIR}/dgif_lib.c"
    "${GIFLIB_SRC_DIR}/egif_lib.c"
    "${GIFLIB_SRC_DIR}/gifalloc.c"
    "${GIFLIB_SRC_DIR}/gif_err.c"
    "${GIFLIB_SRC_DIR}/gif_font.c"
    "${GIFLIB_SRC_DIR}/gif_hash.c"
    "${GIFLIB_SRC_DIR}/openbsd-reallocarray.c"
)
if(WIN32)
    if(BUILD_SHARED_LIBS)
        set_property(TARGET gif PROPERTY PREFIX "")
        target_compile_definitions(gif INTERFACE USE_GIF_DLL)
    else()
        target_compile_definitions(gif PUBLIC USE_GIF_LIB)
    endif()
endif()
if(MSVC)
    find_package(getopt-for-visual-studio REQUIRED CONFIG)
    target_link_libraries(gif PRIVATE getopt-for-visual-studio::getopt-for-visual-studio)
endif()

install(
    TARGETS gif
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
install(
    FILES "${GIFLIB_SRC_DIR}/gif_lib.h"
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

if(UTILS)
    add_library(giflib_util STATIC
        "${GIFLIB_SRC_DIR}/qprintf.c"
        "${GIFLIB_SRC_DIR}/quantize.c"
        "${GIFLIB_SRC_DIR}/getarg.c"
    )
    target_link_libraries(giflib_util PRIVATE gif)

    set(GIF_UTILS
        gif2rgb
        gifbuild
        giffix
        giftext
        giftool
        gifclrmp
    )
    foreach(GIF_UTIL ${GIF_UTILS})
        add_executable(${GIF_UTIL} "${GIFLIB_SRC_DIR}/${GIF_UTIL}.c")
        target_link_libraries(${GIF_UTIL} PRIVATE gif giflib_util)
    endforeach()
    find_library(LIBM NAMES m)
    target_link_libraries(gifclrmp PRIVATE $<$<BOOL:${LIBM}>:${LIBM}>)
    install(TARGETS ${GIF_UTILS} DESTINATION ${CMAKE_INSTALL_BINDIR})
endif()
