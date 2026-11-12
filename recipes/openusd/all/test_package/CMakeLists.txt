cmake_minimum_required(VERSION 3.15)

project(test_package LANGUAGES CXX)

find_package(openusd REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE openusd::openusd)
if(OPENUSD_WITH_IMAGING)
    target_compile_definitions(${PROJECT_NAME} PRIVATE OPENUSD_WITH_IMAGING)
endif()
