cmake_minimum_required(VERSION 3.1)
project(test_package C)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup(TARGETS)

find_package(Argtable3 REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
if(TARGET argtable3)
    target_link_libraries(${PROJECT_NAME} argtable3)
else()
    target_link_libraries(${PROJECT_NAME} argtable3_static)
endif()
