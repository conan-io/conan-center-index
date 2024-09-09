cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES CXX)

find_package(taglib REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE taglib::taglib)
if (taglib_VERSION VERSION_GREATER_EQUAL 2)
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
endif()
