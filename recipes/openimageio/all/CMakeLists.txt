cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper)

include("conanbuildinfo.cmake")
conan_basic_setup(KEEP_RPATHS)

include_directories(
    BEFORE
    # OIIO uses CMAKE_BINARY_DIR, we need to set include dirs
    # in order to be able to use add_subdirectory
    "${CMAKE_BINARY_DIR}/source_subfolder/src/include"
    "${CMAKE_BINARY_DIR}/source_subfolder/include"
    # Same as above but for CMAKE_SOURCE_DIR
    "${CMAKE_SOURCE_DIR}/source_subfolder/src/include"
)

set(CMAKE_INSTALL_SYSTEM_RUNTIME_LIBS_SKIP YES)

add_subdirectory(source_subfolder)
