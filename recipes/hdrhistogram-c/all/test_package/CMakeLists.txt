cmake_minimum_required(VERSION 2.8.11)
project(PackageTest LANGUAGES CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(hdr_decoder_cxx hdr_decoder.cpp)

target_link_libraries(hdr_decoder_cxx ${CONAN_LIBS})
