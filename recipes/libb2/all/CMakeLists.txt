cmake_minimum_required(VERSION 3.4)
project(b2 C)

include("conanbuildinfo.cmake")
conan_basic_setup()

if(WIN32 AND BUILD_SHARED_LIBS AND MSVC)
    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()

option(USE_SSE "Optimized for speed on CPUs supporting SSE2, SSSE3, SSE4.1, AVX, or XOP" OFF)
option(USE_NEON "Optimiced for arm CPUs" OFF)

if (USE_NEON)
    message(STATUS "Using neon sources")
    set(SOURCE_FILES source_subfolder/neon/blake2b-neon.c
                     source_subfolder/neon/blake2bp.c
                     source_subfolder/neon/blake2s-neon.c
                     source_subfolder/neon/blake2xb.c
                     source_subfolder/neon/blake2sp.c
                     source_subfolder/neon/blake2xs.c)
elseif (USE_SSE)
    message(STATUS "Using sse sources")
    set(SOURCE_FILES source_subfolder/sse/blake2b.c
                     source_subfolder/sse/blake2bp.c
                     source_subfolder/sse/blake2s.c
                     source_subfolder/sse/blake2sp.c
                     source_subfolder/sse/blake2xb.c
                     source_subfolder/sse/blake2xs.c)
else ()
    message(STATUS "Using ref sources")
    set(SOURCE_FILES source_subfolder/ref/blake2bp-ref.c
	                 source_subfolder/ref/blake2b-ref.c
	                 source_subfolder/ref/blake2sp-ref.c
	                 source_subfolder/ref/blake2s-ref.c
	                 source_subfolder/ref/blake2xb-ref.c
	                 source_subfolder/ref/blake2xs-ref.c)
endif()

add_library(${CMAKE_PROJECT_NAME} ${SOURCE_FILES})
set_target_properties(${CMAKE_PROJECT_NAME} PROPERTIES PUBLIC_HEADER source_subfolder/ref/blake2.h)

install(TARGETS ${CMAKE_PROJECT_NAME}
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/libb2
        )
