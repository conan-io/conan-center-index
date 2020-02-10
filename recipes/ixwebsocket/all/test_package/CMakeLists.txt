cmake_minimum_required(VERSION 2.8.12)
project(PackageTest CXX)

set (CMAKE_CXX_STANDARD 14)
set (CMAKE_CXX_STANDARD_REQUIRED ON)
set (CMAKE_CXX_EXTENSIONS OFF)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(tests SimpleTests.cpp)

target_link_libraries(tests ${CONAN_LIBS})

