cmake_minimum_required(VERSION 2.8.12)
project(gif C)

include("${CMAKE_CURRENT_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup()

set(SOURCE_FILES
    "source_subfolder/dgif_lib.c"
    "source_subfolder/egif_lib.c"
    "source_subfolder/gifalloc.c"
    "source_subfolder/gif_err.c"
    "source_subfolder/gif_font.c"
    "source_subfolder/gif_hash.c"
    "source_subfolder/openbsd-reallocarray.c"
)

if(NOT BUILD_SHARED_LIBS)
    add_definitions(-DUSE_GIF_LIB)
endif()

add_library(${PROJECT_NAME} ${SOURCE_FILES})
if(WIN32 AND BUILD_SHARED_LIBS)
    set_property(TARGET ${PROJECT_NAME} PROPERTY PREFIX "")
endif()

set(GIF_UTILS
    gif2rgb
    gifbuild
    giffix
    giftext
    giftool
    gifclrmp
)

add_library(giflib_util STATIC
    "source_subfolder/qprintf.c"
    "source_subfolder/quantize.c"
    "source_subfolder/getarg.c"
)
target_link_libraries(giflib_util PRIVATE ${PROJECT_NAME})

foreach(GIF_UTIL ${GIF_UTILS})
    add_executable(${GIF_UTIL} "source_subfolder/${GIF_UTIL}.c")
    target_link_libraries(${GIF_UTIL} PRIVATE ${PROJECT_NAME} giflib_util)
endforeach()
find_library(M_LIBRARY NAMES m)
if(M_LIBRARY)
    target_link_libraries(gifclrmp PRIVATE ${M_LIBRARY})
endif()

install(TARGETS ${PROJECT_NAME} ${GIF_UTILS}
        ARCHIVE DESTINATION "lib"
        LIBRARY DESTINATION "lib"
        RUNTIME DESTINATION "bin"
        BUNDLE DESTINATION "bin")
install(FILES "source_subfolder/gif_lib.h" DESTINATION "include")
