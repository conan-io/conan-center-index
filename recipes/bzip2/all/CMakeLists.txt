cmake_minimum_required(VERSION 3.4)
project(bzip2 C)

include(GNUInstallDirs)

if(MSVC OR MSVC90 OR MSVC10)
    set(MSVC ON)
    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()

set(SOURCE_SUBFOLDER ${CMAKE_CURRENT_SOURCE_DIR}/src)
set(BZ2_LIBRARY bz2)

option(BZ2_BUILD_EXE ON)

set(BZ2_TARGETS ${BZ2_LIBRARY})

add_library(${BZ2_LIBRARY}  ${SOURCE_SUBFOLDER}/blocksort.c
                            ${SOURCE_SUBFOLDER}/bzlib.c
                            ${SOURCE_SUBFOLDER}/compress.c
                            ${SOURCE_SUBFOLDER}/crctable.c
                            ${SOURCE_SUBFOLDER}/decompress.c
                            ${SOURCE_SUBFOLDER}/huffman.c
                            ${SOURCE_SUBFOLDER}/randtable.c
                            ${SOURCE_SUBFOLDER}/bzlib.h
                            ${SOURCE_SUBFOLDER}/bzlib_private.h)
target_include_directories(${BZ2_LIBRARY} PRIVATE ${SOURCE_SUBFOLDER})

if(BZ2_BUILD_EXE)
    add_executable(${CMAKE_PROJECT_NAME} ${SOURCE_SUBFOLDER}/bzip2.c)
    target_link_libraries(${CMAKE_PROJECT_NAME} ${BZ2_LIBRARY})
    target_include_directories(${CMAKE_PROJECT_NAME} PRIVATE ${SOURCE_SUBFOLDER})
    list(APPEND BZ2_TARGETS ${CMAKE_PROJECT_NAME})
endif()

set_target_properties(${BZ2_LIBRARY} PROPERTIES VERSION ${BZ2_VERSION_STRING} SOVERSION ${BZ2_VERSION_MAJOR})

install(TARGETS ${BZ2_TARGETS}
        BUNDLE DESTINATION ${CMAKE_INSTALL_BINDIR}
        RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR})

install(FILES ${SOURCE_SUBFOLDER}/bzlib.h DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
