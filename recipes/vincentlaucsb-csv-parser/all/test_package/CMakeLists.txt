cmake_minimum_required(VERSION 3.9)
project(test_package)

find_package(vincentlaucsb-csv-parser REQUIRED)
add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE vincentlaucsb-csv-parser::vincentlaucsb-csv-parser)
