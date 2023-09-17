cmake_minimum_required(VERSION 3.8)
project(test_package CXX)

find_package(Platform.Converters CONFIG REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE Platform.Converters::Platform.Converters)
set_target_properties(${PROJECT_NAME} PROPERTIES CXX_STANDARD 20)
