cmake_minimum_required(VERSION 3.15)
project(bzip2 LANGUAGES C)

include(GNUInstallDirs)

option(BZ2_BUILD_EXE "Build bzip2 command-line utilities" ON)

add_library(
    bz2
    ${BZ2_SRC_DIR}/blocksort.c
    ${BZ2_SRC_DIR}/bzlib.c
    ${BZ2_SRC_DIR}/compress.c
    ${BZ2_SRC_DIR}/crctable.c
    ${BZ2_SRC_DIR}/decompress.c
    ${BZ2_SRC_DIR}/huffman.c
    ${BZ2_SRC_DIR}/randtable.c
)

target_include_directories(bz2 PUBLIC ${BZ2_SRC_DIR})
set_target_properties(
    bz2
    PROPERTIES
    PUBLIC_HEADER "${BZ2_SRC_DIR}/bzlib.h"
    SOVERSION ${BZ2_VERSION_MAJOR}
    VERSION ${BZ2_VERSION_STRING}
    WINDOWS_EXPORT_ALL_SYMBOLS ON
)

install(
    TARGETS bz2
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

if(BZ2_BUILD_EXE)
    # Main bzip2 executable
    add_executable(bzip2 ${BZ2_SRC_DIR}/bzip2.c)
    target_link_libraries(bzip2 PRIVATE bz2)
    install(TARGETS bzip2 DESTINATION ${CMAKE_INSTALL_BINDIR})

    # bzip2recover utility
    add_executable(bzip2recover ${BZ2_SRC_DIR}/bzip2recover.c)
    target_link_libraries(bzip2recover PRIVATE bz2)
    install(TARGETS bzip2recover DESTINATION ${CMAKE_INSTALL_BINDIR})

    # Install utility scripts
    install(PROGRAMS ${BZ2_SRC_DIR}/bzgrep DESTINATION ${CMAKE_INSTALL_BINDIR})
    install(PROGRAMS ${BZ2_SRC_DIR}/bzmore DESTINATION ${CMAKE_INSTALL_BINDIR})
    install(PROGRAMS ${BZ2_SRC_DIR}/bzdiff DESTINATION ${CMAKE_INSTALL_BINDIR})

    # Install extra tools which are either copies or symlinks of other tools
    # This is a 1:1 mapping of what the original makefile does.
    # bunzip2 and bzcat are copies of bzip2 (not symlinks)
    install(CODE "
        execute_process(COMMAND \${CMAKE_COMMAND} -E copy
            \"\${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_BINDIR}/bzip2${CMAKE_EXECUTABLE_SUFFIX}\"
            \"\${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_BINDIR}/bunzip2${CMAKE_EXECUTABLE_SUFFIX}\")
        execute_process(COMMAND \${CMAKE_COMMAND} -E copy
            \"\${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_BINDIR}/bzip2${CMAKE_EXECUTABLE_SUFFIX}\"
            \"\${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_BINDIR}/bzcat${CMAKE_EXECUTABLE_SUFFIX}\")
    ")

    # Create symlinks
    install(CODE "
        file(CREATE_LINK bzgrep${CMAKE_EXECUTABLE_SUFFIX}
             \"\${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_BINDIR}/bzegrep${CMAKE_EXECUTABLE_SUFFIX}\" SYMBOLIC)
        file(CREATE_LINK bzgrep${CMAKE_EXECUTABLE_SUFFIX}
             \"\${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_BINDIR}/bzfgrep${CMAKE_EXECUTABLE_SUFFIX}\" SYMBOLIC)
        file(CREATE_LINK bzmore${CMAKE_EXECUTABLE_SUFFIX}
            \"\${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_BINDIR}/bzless${CMAKE_EXECUTABLE_SUFFIX}\" SYMBOLIC)
        file(CREATE_LINK bzdiff${CMAKE_EXECUTABLE_SUFFIX}
             \"\${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_BINDIR}/bzcmp${CMAKE_EXECUTABLE_SUFFIX}\" SYMBOLIC)
    ")
endif()
