cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES CXX)

option(built_contrib "Enabled if opencv is built contrib sfm" OFF)

find_package(OpenCV REQUIRED core imgproc CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE opencv_core opencv_imgproc $<TARGET_NAME_IF_EXISTS:opencv_sfm>)
if(built_contrib)
    target_compile_definitions(${PROJECT_NAME} PRIVATE BUILT_CONTRIB)
endif()
