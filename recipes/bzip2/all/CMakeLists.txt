cmake_minimum_required(VERSION 3.4)
project(bzip2 LANGUAGES C)

include(GNUInstallDirs)

option(BZ2_BUILD_EXE "Build bzip2 utility" ON)

add_library(bz2
    ${BZ2_SRC_DIR}/blocksort.c
    ${BZ2_SRC_DIR}/bzlib.c
    ${BZ2_SRC_DIR}/compress.c
    ${BZ2_SRC_DIR}/crctable.c
    ${BZ2_SRC_DIR}/decompress.c
    ${BZ2_SRC_DIR}/huffman.c
    ${BZ2_SRC_DIR}/randtable.c
)
target_include_directories(bz2 PUBLIC ${BZ2_SRC_DIR})
set_target_properties(bz2 PROPERTIES
    VERSION ${BZ2_VERSION_STRING}
    SOVERSION ${BZ2_VERSION_MAJOR}
    WINDOWS_EXPORT_ALL_SYMBOLS ON
)

install(
    TARGETS bz2
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)
install(FILES ${BZ2_SRC_DIR}/bzlib.h DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})

if(BZ2_BUILD_EXE)
    add_executable(bzip2 ${BZ2_SRC_DIR}/bzip2.c)
    target_link_libraries(bzip2 PRIVATE bz2)
    install(TARGETS bzip2 DESTINATION ${CMAKE_INSTALL_BINDIR})
endif()
