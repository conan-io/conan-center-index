cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_library(glslang INTERFACE) # fake target for upstream CMakeLists (glslang required by tests only)

add_library(SPIRV-Tools INTERFACE)
add_library(SPIRV-Tools-opt INTERFACE)
target_link_libraries(SPIRV-Tools INTERFACE CONAN_PKG::spirv-tools)
target_link_libraries(SPIRV-Tools-opt INTERFACE CONAN_PKG::spirv-tools)

add_subdirectory(source_subfolder)
