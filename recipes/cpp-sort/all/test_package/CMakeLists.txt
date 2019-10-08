cmake_minimum_required(VERSION 2.8.11)

project(test_package LANGUAGES CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(${PROJECT_NAME} cpp-sort-integrity.cpp)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
