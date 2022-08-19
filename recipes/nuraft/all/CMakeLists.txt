cmake_minimum_required(VERSION 3.11)
project(nuraft)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(Boost REQUIRED)
find_package(OpenSSL REQUIRED)

add_subdirectory("source_subfolder")
