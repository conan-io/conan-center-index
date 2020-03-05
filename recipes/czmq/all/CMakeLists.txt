cmake_minimum_required(VERSION 2.8.12)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

if(MSVC)
    add_definitions("-D_NOEXCEPT=noexcept")
endif()

if(NOT BUILD_SHARED_LIBS)
    add_definitions("-DCZMQ_STATIC")
endif()

add_subdirectory(source_subfolder)

foreach(TARGET zmakecert zsp test_randof czmq_selftest)
    set_target_properties("${TARGET}"
        PROPERTIES EXCLUDE_FROM_ALL ON)
endforeach()
