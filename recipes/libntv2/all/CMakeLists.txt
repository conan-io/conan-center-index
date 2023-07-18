cmake_minimum_required(VERSION 3.15)

project(libntv2 LANGUAGES C)

option(NTV2_NO_MUTEXES "Disables mutexes" OFF)

add_library(ntv2)

set(NTV2_INCLUDE_DIR ${NTV2_ROOT_DIR}/include)
set(NTV2_SRC_DIR ${NTV2_ROOT_DIR}/src)

target_sources(
    ntv2
    PRIVATE
        "${NTV2_SRC_DIR}/libntv2.c"
        "${NTV2_SRC_DIR}/libntv2_utils.i"
        $<$<BOOL:${WIN32}>:
            "${NTV2_SRC_DIR}/libntv2.def"
            "${NTV2_SRC_DIR}/libntv2.rc"
        >
)

target_include_directories(
    ntv2
    PUBLIC
        ${NTV2_INCLUDE_DIR}
)

set_target_properties(
    ntv2
    PROPERTIES
        PUBLIC_HEADER "${NTV2_INCLUDE_DIR}/libntv2.h"
        C_EXTENSIONS OFF
)

if(NOT NTV2_NO_MUTEXES)
    find_package(Threads REQUIRED)

    target_link_libraries(
        ntv2
        PRIVATE
            Threads::Threads
    )
else()
    target_compile_definitions(
        ntv2
        PRIVATE
            NTV2_NO_MUTEXES
    )
endif()

find_library(LIBM m)
target_link_libraries(ntv2 PRIVATE $<$<BOOL:${LIBM}>:${LIBM}>)

include(GNUInstallDirs)
install(
    TARGETS ntv2
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)
