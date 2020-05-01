cmake_minimum_required(VERSION 3.2)
project(PackageTest)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(example example.cpp example.hpp)
target_link_libraries(example ${CONAN_LIBS})
set_property(TARGET example PROPERTY CXX_STANDARD 17)
