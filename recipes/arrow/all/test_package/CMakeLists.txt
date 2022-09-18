cmake_minimum_required(VERSION 3.8)
project(test_package)

project(test_package CXX)

find_package(Arrow REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} arrow::arrow)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
target_compile_definitions(${PROJECT_NAME} PRIVATE WITH_JEMALLOC)
