cmake_minimum_required(VERSION 3.5.1)
project(conan_cmake_wrapper LANGUAGES C)

set(CMAKE_C_STANDARD 99)
include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup()
set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)

# Source code
set(LLHTTP_SOURCES
  source_subfolder/src/llhttp.c
  source_subfolder/src/http.c
  source_subfolder/src/api.c
)

add_library(llhttp ${LLHTTP_SOURCES})
add_library(llhttp::llhttp ALIAS llhttp)

target_include_directories(llhttp PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/include>
  $<INSTALL_INTERFACE:include>
)

install(TARGETS llhttp
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin)

install(FILES source_subfolder/include/llhttp.h
    DESTINATION include)
