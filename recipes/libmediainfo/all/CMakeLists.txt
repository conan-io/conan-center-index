cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)

add_definitions(${CONAN_DEFINES})
set(ZenLib_LIBRARY ${CONAN_LIBS_LIBZEN})
set(TinyXML_FOUND ON)

add_subdirectory(source_subfolder/Project/CMake)
