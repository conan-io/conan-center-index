cmake_minimum_required(VERSION 3.18)
project(stb LANGUAGES CXX)

add_library(${PROJECT_NAME})
target_include_directories(${PROJECT_NAME} PRIVATE "${CMAKE_SOURCE_DIR}")

if(STB_IMAGE)
    target_sources(${PROJECT_NAME} PRIVATE "stb_image.cpp")
endif()
