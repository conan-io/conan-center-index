cmake_minimum_required(VERSION 3.8)

project(test_package C) # if the project is pure C
project(test_package CXX) # if the project uses c++

find_package(package REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
# don't link to ${CONAN_LIBS} or CONAN_PKG::package
target_link_libraries(${PROJECT_NAME} PRIVATE package::package)
