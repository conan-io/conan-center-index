cmake_minimum_required(VERSION 2.8.12)
project(cmake_wrapper)

set(CONAN_BASIC_SETUP_ARGS)
if(APPLE)
    # When building shared libraries,
    # the binaries in the build tree need RPATHS.
    # No longer required since at least 2.5.2, but it doesn't hurt
    list(APPEND CONAN_BASIC_SETUP_ARGS KEEP_RPATHS)
    set(CMAKE_SKIP_INSTALL_RPATH 1)
endif()

include(conanbuildinfo.cmake)
conan_basic_setup(${CONAN_BASIC_SETUP_ARGS})

add_subdirectory(source_subfolder)
