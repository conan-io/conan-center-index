cmake_minimum_required(VERSION 3.2)
project(cmake_wrapper)

include(BuildUtils.cmake)

include(conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(imgui REQUIRED)
find_package(diligent-core REQUIRED)

add_subdirectory(source_subfolder)
