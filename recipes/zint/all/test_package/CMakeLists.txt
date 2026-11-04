cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

find_package(Zint REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE Zint::Zint)

if(ZINT_WITH_QT)
    enable_language(CXX)
    add_executable(${PROJECT_NAME}_cpp test_package.cpp)
    target_link_libraries(${PROJECT_NAME}_cpp PRIVATE Zint::QZint)
endif()
