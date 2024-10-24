cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

# keep close to the upstream example docs
find_package(PDAL REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PDAL::PDAL)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
