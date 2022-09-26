cmake_minimum_required(VERSION 3.4)
project(dr_wav LANGUAGES C)

include(GNUInstallDirs)

option(NO_CONVERSION_API "Build with define DR_WAV_NO_CONVERSION_API" OFF)
option(NO_STDIO "Build with define DR_WAV_NO_STDIO" OFF)
option(NO_WCHAR "Build with define DR_WAV_NO_WCHAR" OFF)

add_library(dr_wav dr_wav.c)

target_include_directories(dr_wav PRIVATE ${DRWAV_SRC_DIR})

set_target_properties(dr_wav PROPERTIES 
    PUBLIC_HEADER ${DRWAV_SRC_DIR}/dr_wav.h
    C_STANDARD 99
)

if(BUILD_SHARED_LIBS)
    target_compile_definitions(dr_wav PUBLIC -DDRWAV_DLL)
endif()
if(NO_CONVERSION_API)
    target_compile_definitions(dr_wav PUBLIC -DDR_WAV_NO_CONVERSION_API)
endif()
if(NO_STDIO)
    target_compile_definitions(dr_wav PUBLIC -DDR_WAV_NO_STDIO)
endif()
if(NO_WCHAR)
    target_compile_definitions(dr_wav PUBLIC -DDR_WAV_NO_WCHAR)
endif()

install(TARGETS dr_wav
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)
