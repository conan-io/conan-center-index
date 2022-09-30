cmake_minimum_required(VERSION 3.1)
project(PackageTest C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(PkgConfig REQUIRED)
pkg_check_modules(CAP REQUIRED IMPORTED_TARGET libcap)

add_executable(example ../test_package/example.c)
target_link_libraries(example PRIVATE PkgConfig::CAP)
