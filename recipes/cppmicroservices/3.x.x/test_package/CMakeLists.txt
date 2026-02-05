cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

include(GenerateExportHeader)
include(GNUInstallDirs)

find_package(CppMicroServices NO_MODULE REQUIRED)
include(usFrameworkConfig)
include(usServiceComponentConfig)
include(ususAsyncWorkServiceConfig)
include(usDeclarativeServicesConfig)
include(usShellServiceConfig)
include(CppMicroServicesConfig)

set(CMAKE_CXX_VISIBILITY_PRESET hidden)
set(CMAKE_VISIBILITY_INLINES_HIDDEN 1)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

set(CMAKE_CXX_STANDARD 17)

# Output artifacts (executables, shared libraries, and static libraries) to 
# single top-level directories ('bin' or 'lib') in the out-of-source build folder
# (rather than the default behavior of mirroring the source folder hierarchy).
# This is a simple solution to ensure that test executables live in the same directory
# as generated dlls (when building shared libraries on Windows).
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib")
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib")

add_subdirectory(test_bundle)
add_subdirectory(test_app)
