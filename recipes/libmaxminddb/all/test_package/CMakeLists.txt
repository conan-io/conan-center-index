cmake_minimum_required(VERSION 3.1)
project(test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(PkgConfig)
pkg_check_modules(libmaxminddb REQUIRED IMPORTED_TARGET GLOBAL libmaxminddb)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PkgConfig::libmaxminddb)
