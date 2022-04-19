cmake_minimum_required(VERSION 3.4)
project(dr_wav C)

include(conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)

option(NO_CONVERSION_API "Build with define DR_WAV_NO_CONVERSION_API" OFF)
option(NO_STDIO "Build with define DR_WAV_NO_STDIO" OFF)

add_library(${CMAKE_PROJECT_NAME} dr_wav.c)

target_include_directories(${CMAKE_PROJECT_NAME} PRIVATE source_subfolder)

set_target_properties(${CMAKE_PROJECT_NAME} PROPERTIES 
    PUBLIC_HEADER source_subfolder/dr_wav.h
    C_STANDARD 99
)

if(BUILD_SHARED_LIBS)
    target_compile_definitions(${CMAKE_PROJECT_NAME} PUBLIC -DDRWAV_DLL)
endif()
if(NO_CONVERSION_API)
    target_compile_definitions(${CMAKE_PROJECT_NAME} PUBLIC -DDR_WAV_NO_CONVERSION_API)
endif()
if(NO_STDIO)
    target_compile_definitions(${CMAKE_PROJECT_NAME} PUBLIC -DDR_WAV_NO_STDIO)
endif()

install(TARGETS ${CMAKE_PROJECT_NAME}
    RUNTIME DESTINATION bin
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    PUBLIC_HEADER DESTINATION include
)
