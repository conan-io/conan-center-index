cmake_minimum_required(VERSION 3.2)
project(cmake_wrapper)

find_package(SPIRV-Tools REQUIRED CONFIG)
find_package(spirv-cross REQUIRED CONFIG)
find_package(glslang REQUIRED CONFIG)
find_package(volk REQUIRED CONFIG)
find_package(xxHash REQUIRED CONFIG)

add_library(glslang INTERFACE)
target_link_libraries(glslang INTERFACE glslang::glslang)
target_include_directories(glslang INTERFACE ${glslang_INCLUDE_DIR}/glslang)

add_library(SPIRV ALIAS glslang::SPIRV)
add_library(SPIRV-Headers ALIAS SPIRV-Headers::SPIRV-Headers)

add_library(SPIRV-Tools-opt    ALIAS spirv-tools::spirv-tools)
add_library(spirv-tools-core   ALIAS spirv-tools::spirv-tools)
add_library(SPIRV-Tools-static ALIAS spirv-tools::spirv-tools)

add_subdirectory(source_subfolder)

