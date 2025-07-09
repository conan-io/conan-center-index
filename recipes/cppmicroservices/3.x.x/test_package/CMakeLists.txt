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


# clangd can't find compile_commands.json in build/<configuration> subdirectories so
# link to it from the build/ directory
# TODO: does this work / is it necessary with multi-configuration generators?
if (CMAKE_EXPORT_COMPILE_COMMANDS AND EXISTS "${CMAKE_BINARY_DIR}/compile_commands.json"
    AND NOT "${CMAKE_SOURCE_DIR}/build" STREQUAL "${CMAKE_BINARY_DIR}")
    add_custom_target(copy_compile_commands ALL
        COMMAND ${CMAKE_COMMAND} -E make_directory ${CMAKE_SOURCE_DIR}/build
        COMMAND ${CMAKE_COMMAND} -E copy
            ${CMAKE_BINARY_DIR}/compile_commands.json
            ${CMAKE_SOURCE_DIR}/build/compile_commands.json
        DEPENDS ${CMAKE_BINARY_DIR}/compile_commands.json
    )
endif()
