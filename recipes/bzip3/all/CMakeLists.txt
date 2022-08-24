cmake_minimum_required(VERSION 3.4)
project(bzip3 LANGUAGES C)

option(WITH_THREAD "enable thread" OFF)
option(WITH_UTIL "build and install utility" OFF)

set(BZIP3_INC
    ${BZIP3_SRC_DIR}/include/libbz3.h
)

add_library(bzip3)
target_sources(bzip3 PRIVATE
    ${BZIP3_SRC_DIR}/src/cm.c
    ${BZIP3_SRC_DIR}/src/crc32.c
    ${BZIP3_SRC_DIR}/src/libbz3.c
    ${BZIP3_SRC_DIR}/src/libsais.c
    ${BZIP3_SRC_DIR}/src/lzp.c
    ${BZIP3_SRC_DIR}/src/rle.c
)
target_include_directories(bzip3 PUBLIC ${BZIP3_SRC_DIR}/include)
set_target_properties(bzip3 PROPERTIES
    PUBLIC_HEADER "${BZIP3_INC}"
    WINDOWS_EXPORT_ALL_SYMBOLS ON
    C_EXTENSIONS OFF
)
if (with_thread)
    target_compile_definitions(bzip3 PRIVATE "PTHREAD")
endif()

if (WITH_UTIL)
    add_executable(bzip3_cmd ${BZIP3_SRC_DIR}/src/main.c)
    target_link_libraries(bzip3_cmd bzip3)
    target_compile_definitions(bzip3_cmd PRIVATE "VERSION=\"${VERSION}\"")
    set_target_properties(bzip3_cmd PROPERTIES OUTPUT_NAME "bzip3")
endif()

find_library(LIBM m)
target_link_libraries(bzip3 PRIVATE $<$<BOOL:${LIBM}>:${LIBM}>)

include(GNUInstallDirs)
install(
    TARGETS bzip3
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

if (WITH_UTIL)
    install(TARGETS bzip3_cmd DESTINATION ${CMAKE_INSTALL_BINDIR})
endif()
