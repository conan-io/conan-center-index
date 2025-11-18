cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

find_package(frugen REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)

if(BUILD_SHARED_LIB)
    target_link_libraries(${PROJECT_NAME} PRIVATE frugen::fru-shared)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE frugen::fru-static)
endif()
