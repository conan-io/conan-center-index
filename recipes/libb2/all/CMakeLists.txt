cmake_minimum_required(VERSION 3.12)
project(b2 C)

if(WIN32 AND BUILD_SHARED_LIBS AND MSVC)
    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()

option(USE_SSE "Optimized for speed on CPUs supporting SSE2, SSSE3, SSE4.1, AVX, or XOP" OFF)
option(USE_NEON "Optimiced for arm CPUs" OFF)

set(src ${CMAKE_CURRENT_LIST_DIR}/src)

if (USE_NEON)
    message(STATUS "Using neon sources")
    set(SOURCE_FILES ${src}/neon/blake2b-neon.c
                     ${src}/neon/blake2bp.c
                     ${src}/neon/blake2s-neon.c
                     ${src}/neon/blake2xb.c
                     ${src}/neon/blake2sp.c
                     ${src}/neon/blake2xs.c)
elseif (USE_SSE)
    message(STATUS "Using sse sources")
    set(SOURCE_FILES ${src}/sse/blake2b.c
                     ${src}/sse/blake2bp.c
                     ${src}/sse/blake2s.c
                     ${src}/sse/blake2sp.c
                     ${src}/sse/blake2xb.c
                     ${src}/sse/blake2xs.c)
else ()
    message(STATUS "Using ref sources")
    set(SOURCE_FILES ${src}/ref/blake2bp-ref.c
	                 ${src}/ref/blake2b-ref.c
	                 ${src}/ref/blake2sp-ref.c
	                 ${src}/ref/blake2s-ref.c
	                 ${src}/ref/blake2xb-ref.c
	                 ${src}/ref/blake2xs-ref.c)
endif()

add_library(${CMAKE_PROJECT_NAME} ${SOURCE_FILES})
set_target_properties(${CMAKE_PROJECT_NAME} PROPERTIES PUBLIC_HEADER ${src}/ref/blake2.h)

include(GNUInstallDirs)
install(TARGETS ${CMAKE_PROJECT_NAME}
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
        PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/libb2)
