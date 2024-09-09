cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

enable_testing()

option(ZINT_WITH_QT "Zint has been built with Qt support")
if(ZINT_WITH_QT)
    enable_language(CXX)
endif()

find_package(Zint REQUIRED CONFIG)

add_executable(test_package test_package.c)
target_link_libraries(test_package PRIVATE Zint::Zint)
add_test(NAME test_package COMMAND test_package)

if(ZINT_WITH_QT)
    add_executable(test_package_cpp test_package.cpp)
    target_link_libraries(test_package_cpp PRIVATE Zint::QZint)
    add_test(NAME test_package_cpp COMMAND test_package_cpp)
endif()
