cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES CXX)

find_package(agg REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE agg::agg agg::platform )

set_target_properties(${PROJECT_NAME} PROPERTIES WIN32_EXECUTABLE TRUE)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 17)
