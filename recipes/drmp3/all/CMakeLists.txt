cmake_minimum_required(VERSION 3.4)
project(dr_mp3 LANGUAGES C)

include(GNUInstallDirs)

option(NO_SIMD "Build with define DR_MP3_NO_SIMD" OFF)
option(NO_STDIO "Build with define DR_MP3_NO_STDIO" OFF)

add_library(${CMAKE_PROJECT_NAME} dr_mp3.c)

target_include_directories(${CMAKE_PROJECT_NAME} PRIVATE ${DRMP3_SRC_DIR})

set_target_properties(${CMAKE_PROJECT_NAME} PROPERTIES 
    PUBLIC_HEADER ${DRMP3_SRC_DIR}/dr_mp3.h
    C_STANDARD 99
)

if(BUILD_SHARED_LIBS)
    target_compile_definitions(${CMAKE_PROJECT_NAME} PUBLIC -DDRMP3_DLL)
endif()
if(NO_SIMD)
    target_compile_definitions(${CMAKE_PROJECT_NAME} PUBLIC -DDR_MP3_NO_SIMD)
endif()
if(NO_STDIO)
    target_compile_definitions(${CMAKE_PROJECT_NAME} PUBLIC -DDR_MP3_NO_STDIO)
endif()

install(TARGETS ${CMAKE_PROJECT_NAME}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)
