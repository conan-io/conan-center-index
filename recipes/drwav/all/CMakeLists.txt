cmake_minimum_required(VERSION 3.4)
project(dr_wav C)

include(conanbuildinfo.cmake)
conan_basic_setup()

option(NO_CONVERSION_API "Build with define DR_WAV_NO_CONVERSION_API" OFF)
option(NO_STDIO "Build with define DR_WAV_NO_STDIO" OFF)

add_library(${CMAKE_PROJECT_NAME} source_subfolder/dr_wav.h)

set_source_files_properties(source_subfolder/dr_wav.h PROPERTIES
    LANGUAGE C
)

set_target_properties(${CMAKE_PROJECT_NAME} PROPERTIES 
    PUBLIC_HEADER source_subfolder/dr_wav.h
    LINKER_LANGUAGE C
    C_STANDARD 99
)

target_compile_definitions(${CMAKE_PROJECT_NAME} PRIVATE -DDRWAV_IMPLEMENTATION)

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
