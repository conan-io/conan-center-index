cmake_minimum_required(VERSION 3.1.2)
project(conandiligentcore)

include(conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_subdirectory(source_subfolder)
