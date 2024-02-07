cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(log4cplus REQUIRED CONFIG)

if(log4cplus_VERSION VERSION_GREATER_EQUAL 2)
    add_executable(${PROJECT_NAME} test_package.cpp)
else()
    add_executable(${PROJECT_NAME} test_package_v1.cpp)
endif()
target_link_libraries(${PROJECT_NAME} PRIVATE log4cplus::log4cplus)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
