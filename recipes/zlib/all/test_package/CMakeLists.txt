cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

find_package(ZLIB REQUIRED)

if(WITH_TEST_VSNPRINTF)
    message(STATUS "Testing for vsnprintf support")
    add_compile_definitions(WITH_TEST_VSNPRINTF)
endif()

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE ZLIB::ZLIB)
