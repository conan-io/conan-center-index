cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(miniscript REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE miniscript::miniscript)
if(miniscript_VERSION VERSION_GREATER_EQUAL "1.6.2")
    target_compile_definitions(${PROJECT_NAME} PRIVATE MINISCRIPT_1_6)
endif()
