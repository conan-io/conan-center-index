cmake_minimum_required(VERSION 3.12)
project(cmake_wrapper)

set(CONAN_BASIC_SETUP_ARGS TARGETS)
if(APPLE)
    # When building shared libraries,
    # the binaries in the build tree need RPATHS.
    list(APPEND CONAN_BASIC_SETUP_ARGS KEEP_RPATHS)
    set(CMAKE_SKIP_INSTALL_RPATH 1)
endif()

include("${CMAKE_CURRENT_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup(${CONAN_BASIC_SETUP_ARGS})

include_directories(
    BEFORE
    "${CMAKE_SOURCE_DIR}/source_subfolder/src/include"
    "${CMAKE_BINARY_DIR}/source_subfolder/src/include"
    "${CMAKE_BINARY_DIR}/source_subfolder/include"
)

set(CMAKE_OBJECT_PATH_MAX 200)

add_subdirectory(source_subfolder)
