cmake_minimum_required(VERSION 3.15)
project(twolame LANGUAGES C)

include(GNUInstallDirs)

option(BUILD_SHARED_LIBS "Build shared library" OFF)

file(GLOB TWOLAME_SRCS ${TWOLAME_SRC_DIR}/libtwolame/*.c)
file(GLOB TWOLAME_PRIVATE_HDRS ${TWOLAME_SRC_DIR}/libtwolame/*.h)
set(TWOLAME_PUBLIC_HDRS ${TWOLAME_SRC_DIR}/libtwolame/twolame.h)

add_library(twolame ${TWOLAME_SRCS})

target_include_directories(twolame
    PUBLIC  $<BUILD_INTERFACE:${TWOLAME_SRC_DIR}/libtwolame>
            $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
    PRIVATE ${TWOLAME_SRC_DIR}/libtwolame
)

target_compile_definitions(twolame PRIVATE LIBTWOLAME_BUILD)
if(BUILD_SHARED_LIBS)
    target_compile_definitions(twolame PRIVATE DLL_EXPORT)
else()
    target_compile_definitions(twolame PUBLIC LIBTWOLAME_STATIC)
endif()

if(MSVC)
    target_compile_definitions(twolame PRIVATE _CRT_SECURE_NO_WARNINGS)
endif()

if(UNIX)
    target_link_libraries(twolame PRIVATE m)
endif()

set_target_properties(twolame PROPERTIES
    C_STANDARD 99
    PUBLIC_HEADER "${TWOLAME_PUBLIC_HDRS}"
)

install(TARGETS twolame
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)
