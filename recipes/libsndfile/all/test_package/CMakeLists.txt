cmake_minimum_required(VERSION 3.1)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(SndFile REQUIRED)

add_executable(example example.cpp)
target_link_libraries(example PRIVATE SndFile::sndfile)
