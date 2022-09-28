cmake_minimum_required(VERSION 3.8)
project(test_package CXX)

find_package(Trantor CONFIG REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} Trantor::Trantor)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
