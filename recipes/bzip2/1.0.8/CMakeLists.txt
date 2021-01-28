cmake_minimum_required(VERSION 3.4)
project(bzip2 C)

include(GNUInstallDirs)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

if(MSVC OR MSVC90 OR MSVC10)
    set(MSVC ON)
    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)
endif()

set(SOURCE_SUBFOLDER ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder)
set(BZ2_LIBRARY bz2)
set(BZ2_NAMESPACE BZip2)
set(BZ2_CONFIG ${BZ2_NAMESPACE}Config)

option(BZ2_BUILD_EXE OFF)

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
endif()

set_target_properties(${BZ2_LIBRARY} PROPERTIES VERSION ${BZ2_VERSION_STRING} SOVERSION ${BZ2_VERSION_MAJOR})

export(TARGETS ${BZ2_LIBRARY}
       NAMESPACE ${BZ2_NAMESPACE}::
       FILE "${CMAKE_CURRENT_BINARY_DIR}/${BZ2_CONFIG}.cmake")

install(TARGETS ${BZ2_LIBRARY}
        EXPORT ${BZ2_CONFIG}
        RUNTIME DESTINATION bin
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib)

if(BZ2_BUILD_EXE)
    install(TARGETS ${CMAKE_PROJECT_NAME}
            EXPORT ${BZ2_CONFIG}
            BUNDLE DESTINATION bin
            RUNTIME DESTINATION bin
            LIBRARY DESTINATION lib
            ARCHIVE DESTINATION lib)
endif()

install(FILES ${SOURCE_SUBFOLDER}/bzlib.h DESTINATION include)

install(EXPORT ${BZ2_CONFIG}
        DESTINATION "${CMAKE_INSTALL_LIBDIR}/cmake/${CMAKE_PROJECT_NAME}"
        NAMESPACE ${BZ2_LIBRARY}::)
