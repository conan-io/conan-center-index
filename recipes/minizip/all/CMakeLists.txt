cmake_minimum_required(VERSION 3.4)
project(minizip LANGUAGES C)

option(MINIZIP_ENABLE_BZIP2 "Build minizip with bzip2 support" ON)
option(MINIZIP_BUILD_TOOLS "Build minizip tool" OFF)

include(GNUInstallDirs)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${PROJECT_BINARY_DIR}/bin")

find_package(ZLIB REQUIRED)
if(MINIZIP_ENABLE_BZIP2)
    find_package(BZip2 REQUIRED)
endif()

set(SOURCE_FILES
    ${MINIZIP_SRC_DIR}/ioapi.c
    ${MINIZIP_SRC_DIR}/unzip.c
    ${MINIZIP_SRC_DIR}/zip.c
    ${MINIZIP_SRC_DIR}/mztools.c
)
if(WIN32)
    list(APPEND SOURCE_FILES ${MINIZIP_SRC_DIR}/iowin32.c)
endif()

set(HEADER_FILES
    ${MINIZIP_SRC_DIR}/ioapi.h
    ${MINIZIP_SRC_DIR}/unzip.h
    ${MINIZIP_SRC_DIR}/zip.h
    ${MINIZIP_SRC_DIR}/mztools.h
)
if(WIN32)
    list(APPEND HEADER_FILES ${MINIZIP_SRC_DIR}/iowin32.h)
endif()

add_library(minizip ${SOURCE_FILES})
target_link_libraries(minizip PUBLIC ZLIB::ZLIB)
target_compile_definitions(minizip PRIVATE -D_ZLIB_H)
target_include_directories(minizip PUBLIC ${MINIZIP_SRC_DIR})
set_target_properties(minizip PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON)

if(MINIZIP_ENABLE_BZIP2)
    target_compile_definitions(minizip PUBLIC HAVE_BZIP2=1)
    target_link_libraries(minizip PUBLIC BZip2::BZip2)
endif()
if(MSVC)
    target_compile_options(minizip PRIVATE /wd4005 /wd4996 /wd4018 -D_CRT_SECURE_NO_WARNINGS)
endif()

install(
    TARGETS minizip
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

install(FILES ${HEADER_FILES} DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/minizip)

if(MINIZIP_BUILD_TOOLS)
    add_executable(minizip_bin ${MINIZIP_SRC_DIR}/minizip.c)
    add_executable(miniunz_bin ${MINIZIP_SRC_DIR}/miniunz.c)

    target_link_libraries(minizip_bin PRIVATE minizip)
    target_link_libraries(miniunz_bin PRIVATE minizip)

    set_target_properties(minizip_bin PROPERTIES OUTPUT_NAME minizip)
    set_target_properties(miniunz_bin PROPERTIES OUTPUT_NAME miniunz)

    if(MSVC)
        target_compile_options(minizip_bin PRIVATE /wd4005 /wd4996 /wd4018 -D_CRT_SECURE_NO_WARNINGS)
        target_compile_options(miniunz_bin PRIVATE /wd4005 /wd4996 /wd4018 -D_CRT_SECURE_NO_WARNINGS)
    endif()

    install(TARGETS minizip_bin miniunz_bin DESTINATION ${CMAKE_INSTALL_BINDIR})
endif()
