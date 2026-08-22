cmake_minimum_required(VERSION 3.15)
project(test_package)

find_package(GDAL REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} GDAL::GDAL)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)

add_executable(${PROJECT_NAME}_c test_package.c)
target_link_libraries(${PROJECT_NAME}_c GDAL::GDAL)
