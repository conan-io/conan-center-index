cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper C)

include(conanbuildinfo.cmake)
conan_basic_setup(TARGETS KEEP_RPATHS)

find_package(xxHash REQUIRED CONFIG)
link_libraries(xxHash::xxhash)

add_subdirectory(${CONAN_LZ4_CMAKELISTS_SUBFOLDER})
