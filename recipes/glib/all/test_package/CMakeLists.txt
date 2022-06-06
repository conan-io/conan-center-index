cmake_minimum_required(VERSION 3.1)
project(test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(PkgConfig REQUIRED)
pkg_check_modules(glib-2.0 REQUIRED IMPORTED_TARGET glib-2.0)
pkg_check_modules(gio-2.0 REQUIRED IMPORTED_TARGET gio-2.0)
pkg_check_modules(gmodule-2.0 REQUIRED IMPORTED_TARGET gmodule-2.0)
pkg_check_modules(gobject-2.0 REQUIRED IMPORTED_TARGET gobject-2.0)
pkg_check_modules(gthread-2.0 REQUIRED IMPORTED_TARGET gthread-2.0)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PkgConfig::glib-2.0 PkgConfig::gio-2.0 PkgConfig::gmodule-2.0 PkgConfig::gobject-2.0 PkgConfig::gthread-2.0)
