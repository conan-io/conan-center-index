cmake_minimum_required(VERSION 3.15)
project(PackageTest LANGUAGES CXX)

find_package(PkgConfig REQUIRED)
pkg_check_modules(SDBusCpp REQUIRED IMPORTED_TARGET sdbus-c++)

add_executable(example ../test_package/example.cpp)
target_link_libraries(example PRIVATE PkgConfig::SDBusCpp)
