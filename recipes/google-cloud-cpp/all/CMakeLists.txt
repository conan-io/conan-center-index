cmake_minimum_required(VERSION 3.4)
project(cmake_wrapper)

set(CONAN_CMAKE_SILENT_OUTPUT 1)
include(conanbuildinfo.cmake)
conan_basic_setup()

find_package(googleapis REQUIRED CONFIG)
find_package(protobuf REQUIRED CONFIG)
find_package(gRPC REQUIRED CONFIG)

include(googleapis-grpc-libraries.cmake)

set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)

if(MSVC)
    add_definitions("-D_SILENCE_CXX20_REL_OPS_DEPRECATION_WARNING")
    add_definitions("-D_SILENCE_CXX17_CODECVT_HEADER_DEPRECATION_WARNING")
endif()

add_subdirectory("source_subfolder")
