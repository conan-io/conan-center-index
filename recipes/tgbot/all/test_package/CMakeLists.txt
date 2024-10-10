cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(tgbot REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE tgbot::tgbot)
if(tvbot_VERSION VERSION_LESS "1.7.3")
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
else()
    target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
endif()
