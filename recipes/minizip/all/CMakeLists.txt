# This CMake file has been extracted from VCPKG and is under MIT license:
# https://github.com/microsoft/vcpkg/blob/master/ports/minizip/CMakeLists.txt
cmake_minimum_required(VERSION 3.4)
project(minizip C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

option(ENABLE_BZIP2 "Build minizip with bzip2 support" ON)
option(BUILD_TOOLS "Build minizip tool" OFF)

include(GNUInstallDirs)

set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)

set(MIN_SRC "${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/contrib/minizip")
include_directories(${MIN_SRC})

set(SOURCE_FILES
  ${MIN_SRC}/ioapi.c
  ${MIN_SRC}/unzip.c
  ${MIN_SRC}/zip.c
  ${MIN_SRC}/mztools.c
)
if(WIN32)
    list(APPEND SOURCE_FILES ${MIN_SRC}/iowin32.c)
endif()

set(HEADER_FILES
  ${MIN_SRC}/ioapi.h
  ${MIN_SRC}/unzip.h
  ${MIN_SRC}/zip.h
  ${MIN_SRC}/mztools.h
)
if(WIN32)
    list(APPEND HEADER_FILES ${MIN_SRC}/iowin32.h)
endif()

add_library(minizip ${SOURCE_FILES})
target_link_libraries(minizip PUBLIC ${CONAN_LIBS})
target_compile_definitions(minizip PRIVATE -D_ZLIB_H)

if(ENABLE_BZIP2)
    target_compile_definitions(minizip PRIVATE -DHAVE_BZIP2=1)
endif()
if(MSVC)
    target_compile_options(minizip PUBLIC /W3 /wd4005 /wd4996 /wd4018 -D_CRT_SECURE_NO_WARNINGS)
endif()

if (BUILD_TOOLS)
    add_executable(minizip_bin ${MIN_SRC}/minizip.c)
    add_executable(miniunz_bin ${MIN_SRC}/miniunz.c)

    target_link_libraries(minizip_bin minizip ${CONAN_LIBS})
    target_link_libraries(miniunz_bin minizip ${CONAN_LIBS})

    set_target_properties(minizip_bin PROPERTIES OUTPUT_NAME minizip)
    set_target_properties(miniunz_bin PROPERTIES OUTPUT_NAME miniunz)

    if(MSVC)
        target_compile_options(minizip_bin PUBLIC /W3 /wd4005 /wd4996 /wd4018 -D_CRT_SECURE_NO_WARNINGS)
        target_compile_options(miniunz_bin PUBLIC /W3 /wd4005 /wd4996 /wd4018 -D_CRT_SECURE_NO_WARNINGS)
    endif()

    install(TARGETS minizip_bin miniunz_bin DESTINATION ${CMAKE_INSTALL_BINDIR})
endif()

install(
  TARGETS minizip
  RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
  LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
  ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

install(FILES ${HEADER_FILES} DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/minizip)
