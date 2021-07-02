cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
CONAN_BASIC_SETUP(TARGETS)

add_executable(${PROJECT_NAME} sign1.c)
target_link_libraries(${PROJECT_NAME} CONAN_PKG::xmlsec)
