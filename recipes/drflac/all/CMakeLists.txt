cmake_minimum_required(VERSION 3.4)
project(dr_flac C)

include(conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)

set(BUFFER_SIZE "0" CACHE STRING "Value for define DR_FLAC_BUFFER_SIZE. 0 means default buffer size.")
option(NO_CRC "Build with define DR_FLAC_NO_CRC" OFF)
option(NO_OGG "Build with define DR_FLAC_NO_OGG" OFF)
option(NO_SIMD "Build with define DR_FLAC_NO_SIMD" OFF)
option(NO_STDIO "Build with define DR_FLAC_NO_STDIO" OFF)
option(NO_WCHAR "Build with define DR_FLAC_NO_WCHAR" OFF)

add_library(${CMAKE_PROJECT_NAME} dr_flac.c)

target_include_directories(${CMAKE_PROJECT_NAME} PRIVATE source_subfolder)

set_target_properties(${CMAKE_PROJECT_NAME} PROPERTIES 
    PUBLIC_HEADER source_subfolder/dr_flac.h
    C_STANDARD 99
)

if(BUILD_SHARED_LIBS)
    target_compile_definitions(${CMAKE_PROJECT_NAME} PUBLIC -DDRFLAC_DLL)
endif()
if(NOT BUFFER_SIZE STREQUAL "0")
    target_compile_definitions(${CMAKE_PROJECT_NAME} PUBLIC "-DDR_FLAC_BUFFER_SIZE=${BUFFER_SIZE}")
endif()
if(NO_CRC)
    target_compile_definitions(${CMAKE_PROJECT_NAME} PUBLIC -DDR_FLAC_NO_CRC)
endif()
if(NO_OGG)
    target_compile_definitions(${CMAKE_PROJECT_NAME} PUBLIC -DDR_FLAC_NO_OGG)
endif()
if(NO_SIMD)
    target_compile_definitions(${CMAKE_PROJECT_NAME} PUBLIC -DDR_FLAC_NO_SIMD)
endif()
if(NO_STDIO)
    target_compile_definitions(${CMAKE_PROJECT_NAME} PUBLIC -DDR_FLAC_NO_STDIO)
endif()
if(NO_WCHAR)
    target_compile_definitions(${CMAKE_PROJECT_NAME} PUBLIC -DDR_FLAC_NO_WCHAR)
endif()

install(TARGETS ${CMAKE_PROJECT_NAME}
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    PUBLIC_HEADER DESTINATION include
)
