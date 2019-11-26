cmake_minimum_required(VERSION 3.3)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

set(CMAKE_CXX_STANDARD_REQUIRED on)

add_executable(example example.cpp)

# libsolace requires at least C++17
set_target_properties(example PROPERTIES CXX_STANDARD 17)
target_link_libraries(example ${CONAN_LIBS})
