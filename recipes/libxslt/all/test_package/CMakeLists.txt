cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

find_package(LibXslt REQUIRED)
find_package(LibXml2 REQUIRED)

add_executable(${PROJECT_NAME} libxslt_tutorial.c)
target_link_libraries(${PROJECT_NAME} PRIVATE LibXslt::LibXslt LibXml2::LibXml2)
