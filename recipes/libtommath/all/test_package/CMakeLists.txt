cmake_minimum_required(VERSION 3.1)
project(test_package C)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup(TARGETS)

include(FindPkgConfig)
pkg_check_modules(LibTomMath REQUIRED IMPORTED_TARGET libtommath)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE PkgConfig::LibTomMath)
