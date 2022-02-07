cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper)

include(${CMAKE_BINARY_DIR}/../conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(Eigen3 REQUIRED)
find_package(absl REQUIRED)

add_library(NEON_2_SSE INTERFACE IMPORTED)
if (NOT CMAKE_SYSTEM_PROCESSOR OR CMAKE_SYSTEM_PROCESSOR MATCHES "x86")
    set_property(TARGET NEON_2_SSE PROPERTY INTERFACE_LINK_LIBRARIES CONAN_PKG::intel-neon2sse)
endif()

add_library(farmhash INTERFACE IMPORTED)
set_property(TARGET farmhash PROPERTY INTERFACE_LINK_LIBRARIES CONAN_PKG::farmhash)

add_library(fft2d_fftsg2d INTERFACE IMPORTED)
set_property(TARGET fft2d_fftsg2d PROPERTY INTERFACE_LINK_LIBRARIES CONAN_PKG::fft)

add_library(flatbuffers INTERFACE IMPORTED)
set_property(TARGET flatbuffers PROPERTY INTERFACE_LINK_LIBRARIES CONAN_PKG::flatbuffers)

add_library(gemmlowp INTERFACE IMPORTED)
set_property(TARGET gemmlowp PROPERTY INTERFACE_LINK_LIBRARIES CONAN_PKG::gemmlowp)

add_library(ruy INTERFACE IMPORTED)
set_property(TARGET ruy PROPERTY INTERFACE_LINK_LIBRARIES CONAN_PKG::ruy)

add_library(XNNPACK INTERFACE IMPORTED)
set_property(TARGET XNNPACK PROPERTY INTERFACE_LINK_LIBRARIES CONAN_PKG::xnnpack)

add_library(fp16_headers INTERFACE IMPORTED)
set_property(TARGET fp16_headers PROPERTY INTERFACE_LINK_LIBRARIES CONAN_PKG::fp16)

add_subdirectory("source_subfolder/tensorflow/lite")

