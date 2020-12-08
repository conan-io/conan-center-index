cmake_minimum_required(VERSION 3.10.0)
project(PackageTest CXX)
set(CMAKE_CXX_STANDARD 14)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(mgs COMPONENTS base64)
add_executable(example example.cpp)
target_link_libraries(example mgs::base64)
