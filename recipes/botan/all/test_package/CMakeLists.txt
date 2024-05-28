cmake_minimum_required(VERSION 3.15)

project(test_package CXX)

find_package(botan REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} botan::botan)
if(botan_VERSION_STRING VERSION_LESS "3.0.0")
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
else()
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_20)
endif()
