cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(md4qt REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE md4qt::md4qt)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)

if(md4qt_VERSION_STRING VERSION_GREATER_EQUAL "4.0.0")
    target_compile_definitions(${PROJECT_NAME} PRIVATE MD4QT_VERSION_GREATER_EQUAL_4)
endif()
