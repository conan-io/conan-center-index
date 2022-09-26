cmake_minimum_required(VERSION 3.4)
project(dr_mp3 LANGUAGES C)

include(GNUInstallDirs)

option(NO_SIMD "Build with define DR_MP3_NO_SIMD" OFF)
option(NO_STDIO "Build with define DR_MP3_NO_STDIO" OFF)

add_library(dr_mp3 dr_mp3.c)

target_include_directories(dr_mp3 PRIVATE ${DRMP3_SRC_DIR})

set_target_properties(dr_mp3 PROPERTIES 
    PUBLIC_HEADER ${DRMP3_SRC_DIR}/dr_mp3.h
    C_STANDARD 99
)

if(BUILD_SHARED_LIBS)
    target_compile_definitions(dr_mp3 PUBLIC -DDRMP3_DLL)
endif()
if(NO_SIMD)
    target_compile_definitions(dr_mp3 PUBLIC -DDR_MP3_NO_SIMD)
endif()
if(NO_STDIO)
    target_compile_definitions(dr_mp3 PUBLIC -DDR_MP3_NO_STDIO)
endif()

install(TARGETS dr_mp3
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)
