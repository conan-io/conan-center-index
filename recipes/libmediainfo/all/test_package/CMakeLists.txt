cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES CXX)

find_package(MediaInfoLib REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE mediainfo)

option(LIBMEDIAINFO_SHARED "Is libmediainfo a shared library?")
if(LIBMEDIAINFO_SHARED)
    target_compile_definitions(${PROJECT_NAME} PRIVATE LIBMEDIAINFO_SHARED)
endif()
