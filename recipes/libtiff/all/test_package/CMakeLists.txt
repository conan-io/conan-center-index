cmake_minimum_required(VERSION 3.15)
project(test_package C CXX)

find_package(TIFF REQUIRED)

add_executable(${PROJECT_NAME}_c test_package.c)
target_link_libraries(${PROJECT_NAME}_c PRIVATE TIFF::TIFF)

if(TARGET TIFF::CXX)
    add_executable(${PROJECT_NAME}_cxx test_package.cpp)
    target_link_libraries(${PROJECT_NAME}_cxx PRIVATE TIFF::CXX)
endif()
