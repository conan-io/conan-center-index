cmake_minimum_required(VERSION 2.8.12)
project(PackageTest CXX)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

message(STATUS "CONAN_INCLUDE_DIRS is ${CONAN_INCLUDE_DIRS}")
message(STATUS "CONAN_LIBS is ${CONAN_LIBS}")
include_directories(${CONAN_INCLUDE_DIRS})

add_executable(example example.cpp)
target_link_libraries(example ${CONAN_LIBS})