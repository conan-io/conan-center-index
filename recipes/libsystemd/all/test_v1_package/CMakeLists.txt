cmake_minimum_required(VERSION 3.15)
project(PackageTest LANGUAGES C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(PkgConfig REQUIRED)
pkg_check_modules(SYSTEMD REQUIRED IMPORTED_TARGET libsystemd)

add_executable(example ../test_package/example.c)
target_link_libraries(example PRIVATE PkgConfig::SYSTEMD)
