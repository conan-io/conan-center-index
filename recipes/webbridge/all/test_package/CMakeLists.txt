cmake_minimum_required(VERSION 3.26)
project(test_package CXX)

find_package(webbridge REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_20)
target_link_libraries(${PROJECT_NAME} PRIVATE webbridge::webbridge)
