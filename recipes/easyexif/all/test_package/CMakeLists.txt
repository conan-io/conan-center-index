cmake_minimum_required(VERSION 3.1)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(example example.cpp)

set_target_properties(example PROPERTIES CXX_STANDARD 11 CXX_STANDARD_REQUIRED ON)
target_link_libraries(example ${CONAN_LIBS})
