cmake_minimum_required(VERSION 3.1)
project(PackageTest CXX)
set(CMAKE_CXX_STANDARD 11)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup(TARGETS)
find_package(tl-expected REQUIRED)

add_executable(example example.cpp)
target_link_libraries(example tl::expected)
