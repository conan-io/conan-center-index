cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(cmocka REQUIRED CONFIG)

add_executable(${PROJECT_NAME} ../test_package/test_package.c)
target_include_directories(${PROJECT_NAME} PRIVATE ${CMOCKA_INCLUDE_DIR})
target_link_libraries(${PROJECT_NAME} PRIVATE ${CMOCKA_LIBRARY})
