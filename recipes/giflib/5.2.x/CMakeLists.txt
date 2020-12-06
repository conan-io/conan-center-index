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

install(TARGETS ${PROJECT_NAME}
        ARCHIVE DESTINATION "lib"
        LIBRARY DESTINATION "lib"
        RUNTIME DESTINATION "bin")
install(FILES "source_subfolder/gif_lib.h" DESTINATION "include")
