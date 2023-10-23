cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES CXX)

find_package(OpenSubdiv REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
if(TARGET OpenSubdiv::osdcpu_static)
    target_link_libraries(${PROJECT_NAME} PRIVATE OpenSubdiv::osdcpu_static)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE OpenSubdiv::osdcpu)
endif()
