cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

find_package(sundials REQUIRED CONFIG)

if(sundials_VERSION GREATER_EQUAL 6)
    add_executable(${PROJECT_NAME} test_package_v6.c)
else()
    add_executable(${PROJECT_NAME} test_package_v5.c)
endif()
target_link_libraries(${PROJECT_NAME} PRIVATE sundials::sundials)
