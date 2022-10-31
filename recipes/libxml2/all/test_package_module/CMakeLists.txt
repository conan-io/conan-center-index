cmake_minimum_required(VERSION 3.8)
project(test_package C)

find_package(LibXml2 REQUIRED)

add_executable(${PROJECT_NAME} ../test_package/test_package.c)
target_link_libraries(${PROJECT_NAME} LibXml2::LibXml2)
