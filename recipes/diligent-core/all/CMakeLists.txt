cmake_minimum_required(VERSION 3.2)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(SPIRV-Tools REQUIRED CONFIG)
find_package(spirv-cross REQUIRED CONFIG)
find_package(glslang REQUIRED CONFIG)
find_package(volk REQUIRED CONFIG)
find_package(xxHash REQUIRED CONFIG)

add_library(glslang ALIAS glslang::glslang)
add_library(SPIRV-Headers ALIAS SPIRV-Headers::SPIRV-Headers)

get_cmake_property(_variableNames VARIABLES)
list (SORT _variableNames)
foreach (_variableName ${_variableNames})
message(STATUS "${_variableName}=${${_variableName}}")
endforeach()

add_subdirectory(source_subfolder)
