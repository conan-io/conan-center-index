cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(unifex REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE unifex::unifex)
if(MSVC)
    set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 20)
else()
    set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 17)
endif()
