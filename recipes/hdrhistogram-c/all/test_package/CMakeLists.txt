cmake_minimum_required(VERSION 2.8.11)
project(PackageTest LANGUAGES C CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(hdr_decoder_c hdr_decoder.c)
add_executable(hdr_decoder_cxx hdr_decoder.cpp)

target_link_libraries(hdr_decoder_c ${CONAN_LIBS})
target_link_libraries(hdr_decoder_cxx ${CONAN_LIBS})
