cmake_minimum_required(VERSION 3.4)
project(dr_flac LANGUAGES C)

include(GNUInstallDirs)

set(BUFFER_SIZE "0" CACHE STRING "Value for define DR_FLAC_BUFFER_SIZE. 0 means default buffer size.")
option(NO_CRC "Build with define DR_FLAC_NO_CRC" OFF)
option(NO_OGG "Build with define DR_FLAC_NO_OGG" OFF)
option(NO_SIMD "Build with define DR_FLAC_NO_SIMD" OFF)
option(NO_STDIO "Build with define DR_FLAC_NO_STDIO" OFF)
option(NO_WCHAR "Build with define DR_FLAC_NO_WCHAR" OFF)

add_library(dr_flac dr_flac.c)

target_include_directories(dr_flac PRIVATE ${DRFLAC_SRC_DIR})

set_target_properties(dr_flac PROPERTIES 
    PUBLIC_HEADER ${DRFLAC_SRC_DIR}/dr_flac.h
    C_STANDARD 99
)

if(BUILD_SHARED_LIBS)
    target_compile_definitions(dr_flac PUBLIC -DDRFLAC_DLL)
endif()
if(NOT BUFFER_SIZE STREQUAL "0")
    target_compile_definitions(dr_flac PUBLIC "-DDR_FLAC_BUFFER_SIZE=${BUFFER_SIZE}")
endif()
if(NO_CRC)
    target_compile_definitions(dr_flac PUBLIC -DDR_FLAC_NO_CRC)
endif()
if(NO_OGG)
    target_compile_definitions(dr_flac PUBLIC -DDR_FLAC_NO_OGG)
endif()
if(NO_SIMD)
    target_compile_definitions(dr_flac PUBLIC -DDR_FLAC_NO_SIMD)
endif()
if(NO_STDIO)
    target_compile_definitions(dr_flac PUBLIC -DDR_FLAC_NO_STDIO)
endif()
if(NO_WCHAR)
    target_compile_definitions(dr_flac PUBLIC -DDR_FLAC_NO_WCHAR)
endif()

install(TARGETS dr_flac
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)
