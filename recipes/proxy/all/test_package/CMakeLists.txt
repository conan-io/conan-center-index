cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(proxy REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE msft_proxy)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_20)
if(proxy_VERSION VERSION_GREATER_EQUAL "3.0.0")
    target_compile_definitions(${PROJECT_NAME} PRIVATE PROXY_VERSION_3_LATER)
endif()
