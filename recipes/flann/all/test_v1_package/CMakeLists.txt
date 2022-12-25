cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(flann REQUIRED CONFIG)

add_executable(${PROJECT_NAME} ../test_package/test_package.c)
if(TARGET flann::flann_s)
    target_link_libraries(${PROJECT_NAME} PRIVATE flann::flann_s)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE flann::flann)
endif()
