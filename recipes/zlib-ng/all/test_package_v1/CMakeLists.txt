cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_executable(${PROJECT_NAME} ${CMAKE_CURRENT_SOURCE_DIR}/../test_package/test_package.c)
target_link_libraries(${PROJECT_NAME} CONAN_PKG::zlib-ng)
set_property(TARGET ${PROJECT_NAME} PROPERTY C_STANDARD 99)
