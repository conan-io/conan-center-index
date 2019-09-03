cmake_minimum_required(VERSION 2.8.11)
project(test_package C)

set(CMAKE_VERBOSE_MAKEFILE TRUE)

file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/logo.png
     DESTINATION ${CMAKE_CURRENT_BINARY_DIR})

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
