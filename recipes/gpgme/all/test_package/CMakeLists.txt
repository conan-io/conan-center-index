cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

find_package(gpgme REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE gpgme::gpgme)
