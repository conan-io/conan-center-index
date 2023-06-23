cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

if(ENABLE_CXX)
    enable_language(CXX)
endif()

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(gmp REQUIRED CONFIG)

add_executable(${PROJECT_NAME} ../test_package/test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE gmp::GMP)

if(TEST_PIC)
    add_library(${PROJECT_NAME}_shared SHARED ../test_package/test_package.c)
    target_link_libraries(${PROJECT_NAME}_shared PRIVATE gmp::GMP)
endif()

if(ENABLE_CXX)
    add_executable(${PROJECT_NAME}_cpp ../test_package/test_package.cpp)
    target_link_libraries(${PROJECT_NAME}_cpp PRIVATE gmp::GMPXX)
endif()
