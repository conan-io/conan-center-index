cmake_minimum_required(VERSION 2.8.11)
project(PackageTest LANGUAGES C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(hdr_decoder hdr_decoder.c)

target_link_libraries(hdr_decoder ${CONAN_LIBS})
