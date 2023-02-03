cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES CXX)

find_package(plog REQUIRED CONFIG)

add_executable(${CMAKE_PROJECT_NAME} test_package.cpp)
target_link_libraries(${CMAKE_PROJECT_NAME} PRIVATE plog::plog)

if(plog_VERSION VERSION_GREATER_EQUAL "1.1.6")
    target_compile_definitions(${CMAKE_PROJECT_NAME} PRIVATE -DPLOG_EXPLICIT_INIT)
endif()
