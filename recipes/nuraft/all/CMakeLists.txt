cmake_minimum_required(VERSION 3.11)
project(jungle)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(Boost REQUIRED)
find_package(OpenSSL REQUIRED)

enable_testing()

add_subdirectory("source_subfolder")
