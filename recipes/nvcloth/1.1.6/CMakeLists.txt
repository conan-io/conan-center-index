# Using a CMake wrapper because the project's CMakeLists.txt does not set project()
cmake_minimum_required(VERSION 3.15)
project(cmake_wrapper CXX)

add_subdirectory("src/NvCloth/compiler/cmake/${TARGET_BUILD_PLATFORM}")
