cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(trng4 REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE trng4::trng4)
