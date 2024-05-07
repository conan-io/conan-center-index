cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX C)

find_package(shaderc REQUIRED CONFIG)

add_executable(${PROJECT_NAME}_shaderc_c test_package_shaderc.c)
target_link_libraries(${PROJECT_NAME}_shaderc_c PRIVATE shaderc::shaderc)

add_executable(${PROJECT_NAME}_shaderc_cpp test_package_shaderc.cpp)
target_link_libraries(${PROJECT_NAME}_shaderc_cpp PRIVATE shaderc::shaderc)
set_property(TARGET ${PROJECT_NAME}_shaderc_cpp PROPERTY CXX_STANDARD 11)
