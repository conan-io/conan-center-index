cmake_minimum_required(VERSION 3.8)
project(PackageTest CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(sobjectizer REQUIRED CONFIG)

add_executable(example example.cpp)
if(SOBJECTIZER_SHARED)
  target_link_libraries(example sobjectizer::SharedLib)
else()
  target_link_libraries(example sobjectizer::StaticLib)
endif()
