cmake_minimum_required(VERSION 3.4)
project(test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(PkgConfig)
pkg_check_modules(LMDB REQUIRED IMPORTED_TARGET GLOBAL lmdb)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PkgConfig::LMDB)
