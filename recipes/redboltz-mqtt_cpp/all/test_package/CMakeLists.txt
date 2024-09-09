cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(mqtt_cpp REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} mqtt_cpp::mqtt_cpp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
