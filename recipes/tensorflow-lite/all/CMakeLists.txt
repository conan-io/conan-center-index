cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper)

include(${CMAKE_BINARY_DIR}/../conanbuildinfo.cmake)
conan_basic_setup(KEEP_RPATHS)

find_package(Eigen3 REQUIRED)
find_package(absl REQUIRED)

add_library(NEON_2_SSE INTERFACE IMPORTED)
if (NOT CMAKE_SYSTEM_PROCESSOR OR CMAKE_SYSTEM_PROCESSOR MATCHES "x86")
    find_package(NEON_2_SSE REQUIRED)
    set_property(TARGET NEON_2_SSE PROPERTY INTERFACE_LINK_LIBRARIES NEON_2_SSE::NEON_2_SSE)
endif()

find_package(farmhash REQUIRED)
add_library(farmhash INTERFACE IMPORTED)
set_property(TARGET farmhash PROPERTY INTERFACE_LINK_LIBRARIES farmhash::farmhash)

find_package(fft REQUIRED)
add_library(fft2d_fftsg2d INTERFACE IMPORTED)
set_property(TARGET fft2d_fftsg2d PROPERTY INTERFACE_LINK_LIBRARIES fft::fft)

find_package(Flatbuffers REQUIRED)
add_library(flatbuffers INTERFACE IMPORTED)
set_property(TARGET flatbuffers PROPERTY INTERFACE_LINK_LIBRARIES flatbuffers::flatbuffers)

find_package(gemmlowp REQUIRED)
add_library(gemmlowp INTERFACE IMPORTED)
set_property(TARGET gemmlowp PROPERTY INTERFACE_LINK_LIBRARIES gemmlowp::gemmlowp)

find_package(ruy REQUIRED)
add_library(ruy INTERFACE IMPORTED)
set_property(TARGET ruy PROPERTY INTERFACE_LINK_LIBRARIES ruy::ruy)

find_package(xnnpack REQUIRED)
add_library(XNNPACK INTERFACE IMPORTED)
set_property(TARGET XNNPACK PROPERTY INTERFACE_LINK_LIBRARIES xnnpack::xnnpack)

find_package(fp16 REQUIRED)
add_library(fp16_headers INTERFACE IMPORTED)
set_property(TARGET fp16_headers PROPERTY INTERFACE_LINK_LIBRARIES fp16::fp16)

add_subdirectory("src/tensorflow/lite")
