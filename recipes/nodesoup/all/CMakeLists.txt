cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

if(NOT MATPLOTPLUSPLUS_CONAN_FFTW_THREADS)
    add_definitions(-Dcimg_use_fftw3_singlethread=)
endif()

#add_library(cimg INTERFACE)
#target_link_libraries(cimg INTERFACE CImg::CImg)

add_subdirectory(source_subfolder)
