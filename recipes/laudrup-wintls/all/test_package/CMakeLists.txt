cmake_minimum_required(VERSION 3.15)

project(test_package LANGUAGES CXX)

find_package(laudrup-wintls REQUIRED CONFIG)
find_package(boost REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE laudrup-wintls::laudrup-wintls Boost::headers)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
