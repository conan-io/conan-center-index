cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

if ("${CONAN_PACKAGE_VERSION}" VERSION_LESS "2.4.0")
    add_subdirectory("source_subfolder/Box2D")
else()
    add_subdirectory("source_subfolder")
endif()
