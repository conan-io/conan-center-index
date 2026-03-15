cmake_minimum_required(VERSION 3.18)
project(stb LANGUAGES CXX)

set(STB_SOURCES "")
if(STB_IMAGE)
    list(APPEND STB_SOURCES "stb_image.cpp")
endif()

if(STB_SOURCES)
    add_library(${PROJECT_NAME} ${STB_SOURCES})
    target_include_directories(${PROJECT_NAME} PRIVATE "${CMAKE_SOURCE_DIR}")
endif()

