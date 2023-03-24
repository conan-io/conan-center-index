cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

find_package(apr REQUIRED CONFIG)

find_package(apr-util REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_include_directories(${PROJECT_NAME} PRIVATE ${apr_INCLUDE_DIR} ${apr-util_INCLUDE_DIR})
target_link_libraries(${PROJECT_NAME} PRIVATE apr-util::apr-util apr::apr)
