cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

enable_testing()

find_package(gmp REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE gmp::libgmp)
add_test(NAME ${PROJECT_NAME}_test COMMAND ${PROJECT_NAME})

if(TEST_PIC)
    set(CMAKE_POSITION_INDEPENDENT_CODE ON)
    add_executable(${PROJECT_NAME}_pic test_package.c)
    target_link_libraries(${PROJECT_NAME}_pic PRIVATE gmp::libgmp)
    add_test(NAME ${PROJECT_NAME}_pic_test COMMAND ${PROJECT_NAME}_pic)
endif()

if(ENABLE_CXX)
    enable_language(CXX)
    add_executable(${PROJECT_NAME}_cpp test_package.cpp)
    target_link_libraries(${PROJECT_NAME}_cpp PRIVATE gmp::gmpxx)
    add_test(NAME ${PROJECT_NAME}_cpp_test COMMAND ${PROJECT_NAME}_cpp)
endif()
