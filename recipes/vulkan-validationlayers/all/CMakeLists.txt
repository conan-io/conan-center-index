cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_library(glslang INTERFACE)
target_link_libraries(glslang INTERFACE CONAN_PKG::glslang)

add_library(SPIRV-Tools INTERFACE)
target_link_libraries(SPIRV-Tools INTERFACE CONAN_PKG::spirv-tools)

add_subdirectory(source_subfolder)
