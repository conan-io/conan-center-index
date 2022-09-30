cmake_minimum_required(VERSION 3.5)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(qwt REQUIRED)

add_executable(example example.cpp)
# Must compile with "-fPIC" since Qt was built with -reduce-relocations.
target_compile_options(example PRIVATE -fPIC)
target_link_libraries(example CONAN_PKG::qt CONAN_PKG::qwt)
set_property(TARGET example PROPERTY CXX_STANDARD 11)

