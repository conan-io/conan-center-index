cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(cpp-lazy REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE cpp-lazy::cpp-lazy)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
if(cpp-lazy_VERSION VERSION_GREATER_EQUAL "9.0.0")
    target_compile_definitions(${PROJECT_NAME} PRIVATE CPP_LAZY_9_0_0_NEWER)
endif()
