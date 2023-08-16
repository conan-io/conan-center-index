cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(hunspell REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cxx)
target_link_libraries(${PROJECT_NAME} PRIVATE hunspell::hunspell)
