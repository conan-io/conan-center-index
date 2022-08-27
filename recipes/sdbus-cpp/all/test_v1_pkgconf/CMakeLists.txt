cmake_minimum_required(VERSION 3.13)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(PkgConfig REQUIRED)
pkg_check_modules(SDBusCpp REQUIRED IMPORTED_TARGET sdbus-c++)

add_executable(example ../test_package/example.cpp)
target_link_libraries(example PRIVATE PkgConfig::SDBusCpp)
