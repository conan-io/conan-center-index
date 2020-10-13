cmake_minimum_required(VERSION 3.4)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

link_libraries(CONAN_PKG::libusb-compat)
include_directories(${CONAN_INCLUDE_DIRS_BOOST})

add_subdirectory(source_subfolder)
