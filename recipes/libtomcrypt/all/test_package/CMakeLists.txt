cmake_minimum_required(VERSION 3.15)
project(test_package C)

include(FindPkgConfig)
pkg_check_modules(LibTomCrypt REQUIRED IMPORTED_TARGET libtomcrypt)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE PkgConfig::LibTomCrypt)
target_compile_definitions(${PROJECT_NAME} PRIVATE LTC_NO_PROTOTYPES)
