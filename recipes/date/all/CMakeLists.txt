cmake_minimum_required(VERSION 3.0.2)

project(cmake_wrapper)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_subdirectory(source_subfolder)

if (WIN32 AND BUILD_SHARED_LIBS)
    target_compile_definitions( tz PRIVATE DATE_BUILD_DLL=1 )
endif(WIN32 AND BUILD_SHARED_LIBS)