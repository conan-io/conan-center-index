cmake_minimum_required(VERSION 2.8.12)
project(test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_executable(${PROJECT_NAME} example.c)

target_link_libraries(${PROJECT_NAME} CONAN_PKG::libva)
