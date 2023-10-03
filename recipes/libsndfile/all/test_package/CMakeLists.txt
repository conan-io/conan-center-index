cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C CXX)

find_package(SndFile REQUIRED CONFIG)

add_executable(${PROJECT_NAME}_c test_package.c)
target_link_libraries(${PROJECT_NAME}_c PRIVATE SndFile::sndfile)

add_executable(${PROJECT_NAME}_cxx test_package.cpp)
target_link_libraries(${PROJECT_NAME}_cxx PRIVATE SndFile::sndfile)
