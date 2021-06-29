cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

if(CONAN_COMPILER MATCHES "clang" AND CONAN_COMPILER_VERSION VERSION_LESS "4.0")
    add_compile_options(-ftemplate-depth=1024)
endif()

add_subdirectory(source_subfolder)
