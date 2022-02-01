cmake_minimum_required(VERSION 3.1)
project(gif C)

include(conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)

include(GNUInstallDirs)

add_library(gif
    "source_subfolder/dgif_lib.c"
    "source_subfolder/egif_lib.c"
    "source_subfolder/gifalloc.c"
    "source_subfolder/gif_err.c"
    "source_subfolder/gif_font.c"
    "source_subfolder/gif_hash.c"
    "source_subfolder/openbsd-reallocarray.c"
)
if(WIN32)
    if(BUILD_SHARED_LIBS)
        set_property(TARGET gif PROPERTY PREFIX "")
        target_compile_definitions(gif INTERFACE USE_GIF_DLL)
    else()
        target_compile_definitions(gif PUBLIC USE_GIF_LIB)
    endif()
endif()

install(
    TARGETS gif
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
install(
    FILES "source_subfolder/gif_lib.h"
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

if(UTILS)
    add_library(giflib_util STATIC
        "source_subfolder/qprintf.c"
        "source_subfolder/quantize.c"
        "source_subfolder/getarg.c"
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
        add_executable(${GIF_UTIL} "source_subfolder/${GIF_UTIL}.c")
        target_link_libraries(${GIF_UTIL} PRIVATE gif giflib_util)
    endforeach()
    find_library(LIBM NAMES m)
    target_link_libraries(gifclrmp PRIVATE $<$<BOOL:${LIBM}>:${LIBM}>)
    install(TARGETS ${GIF_UTILS} DESTINATION ${CMAKE_INSTALL_BINDIR})
endif()
