cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

find_package(gmp REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE gmp::libgmp)

if(TEST_PIC)
    add_library(${PROJECT_NAME}_shared SHARED test_package.c)
    target_link_libraries(${PROJECT_NAME}_shared PRIVATE gmp::libgmp)
endif()

if(ENABLE_CXX)
    enable_language(CXX)
    add_executable(${PROJECT_NAME}_cpp test_package.cpp)
    target_link_libraries(${PROJECT_NAME}_cpp PRIVATE gmp::gmpxx)
endif()
