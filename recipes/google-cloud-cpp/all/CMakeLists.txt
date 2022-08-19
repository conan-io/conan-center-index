cmake_minimum_required(VERSION 3.4)
project(cmake_wrapper)

set(CONAN_CMAKE_SILENT_OUTPUT 1)
include(conanbuildinfo.cmake)
conan_basic_setup()

find_package(googleapis REQUIRED CONFIG)
find_package(protobuf REQUIRED CONFIG)
find_package(gRPC REQUIRED CONFIG)

set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)

if(MSVC)
    add_definitions("-D_SILENCE_CXX20_REL_OPS_DEPRECATION_WARNING")
    add_definitions("-D_SILENCE_CXX17_CODECVT_HEADER_DEPRECATION_WARNING")
endif()

add_subdirectory("source_subfolder")

# Recover some variables that are not available in this scope, and create targets from googleapis
get_target_property(PROJECT_VERSION google_cloud_cpp_common VERSION)
get_target_property(PROJECT_VERSION_MAJOR google_cloud_cpp_common SOVERSION)
list(APPEND CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR}/source_subfolder/cmake)
include(googleapis-grpc-libraries.cmake)
