cmake_minimum_required(VERSION 3.4)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_library(cpuinfo INTERFACE IMPORTED)
add_library(clog INTERFACE IMPORTED)
set_property(TARGET cpuinfo PROPERTY INTERFACE_LINK_LIBRARIES CONAN_PKG::cpuinfo)
set_property(TARGET clog PROPERTY INTERFACE_LINK_LIBRARIES CONAN_PKG::cpuinfo)

add_library(pthreadpool INTERFACE IMPORTED)
set_property(TARGET pthreadpool PROPERTY INTERFACE_LINK_LIBRARIES CONAN_PKG::pthreadpool)

add_library(fxdiv INTERFACE IMPORTED)
set_property(TARGET fxdiv PROPERTY INTERFACE_LINK_LIBRARIES CONAN_PKG::fxdiv)

add_library(fp16 INTERFACE IMPORTED)
set_property(TARGET fp16 PROPERTY INTERFACE_LINK_LIBRARIES CONAN_PKG::fp16)

if(MSVC AND BUILD_SHARED_LIBS)
    set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS TRUE)
endif()

add_subdirectory(source_subfolder)
