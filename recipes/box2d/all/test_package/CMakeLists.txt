cmake_minimum_required(VERSION 3.21)
project(test_package LANGUAGES C CXX)

find_package(box2d REQUIRED CONFIG)

if(box2d_VERSION VERSION_LESS "3.0.0")
    add_executable(${PROJECT_NAME} test_package.cpp)
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
else()
    add_executable(${PROJECT_NAME} test_package3.c)
    target_compile_features(${PROJECT_NAME} PRIVATE c_std_17)
endif()
target_link_libraries(${PROJECT_NAME} PRIVATE box2d::box2d)
