cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_library(asmjit INTERFACE IMPORTED)
set_property(TARGET asmjit PROPERTY INTERFACE_LINK_LIBRARIES CONAN_PKG::asmjit)

add_library(cpuinfo INTERFACE IMPORTED)
set_property(TARGET cpuinfo PROPERTY INTERFACE_LINK_LIBRARIES CONAN_PKG::cpuinfo)

add_subdirectory(source_subfolder)
