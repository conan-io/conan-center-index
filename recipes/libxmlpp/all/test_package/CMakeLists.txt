cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(libxmlpp REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE libxmlpp::libxmlpp)
if(libxmlpp_VERSION VERSION_GREATER_EQUAL "5.4.0")
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
else()
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
endif()
