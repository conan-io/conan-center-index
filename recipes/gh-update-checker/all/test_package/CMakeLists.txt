cmake_minimum_required(VERSION 3.23)

project(gh_update_checker_test_package LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(gh_update_checker REQUIRED CONFIG)

add_executable(gh-update-checker-test src/gh-update-checker.cpp)
target_link_libraries(gh-update-checker-test PRIVATE gh_update_checker::gh_update_checker)
