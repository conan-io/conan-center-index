cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

# keep close to the upstream example docs
find_package(PDAL REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PDAL::PDAL)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
