cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C CXX)

find_package(GDAL REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE GDAL::GDAL)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)

add_executable(${PROJECT_NAME}_c test_package.c)
target_link_libraries(${PROJECT_NAME}_c PRIVATE GDAL::GDAL)
