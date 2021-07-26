cmake_minimum_required(VERSION 2.8.12)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

link_libraries(CONAN_PKG::jsoncpp)

add_subdirectory(source_subfolder)
