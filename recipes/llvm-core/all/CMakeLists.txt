cmake_minimum_required(VERSION 3.13.4)
project(conanllvm)

include(${CMAKE_CURRENT_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)

list(PREPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")
if(UNIX)
  # LLVM 11.1.0 requires the zlib lib dir to be in the library path.
  # This is not needed for later versions.
  set(ENV{LIBRARY_PATH} "${CONAN_LIB_DIRS_ZLIB}:$ENV{LIBRARY_PATH}")
endif()

add_subdirectory("source")
