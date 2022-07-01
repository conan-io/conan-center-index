cmake_minimum_required(VERSION 3.1)
project(test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(xmlsec REQUIRED CONFIG)

add_executable(${PROJECT_NAME} sign1.c)
target_link_libraries(${PROJECT_NAME} xmlsec::xmlsec)
