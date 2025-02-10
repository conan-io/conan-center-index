cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(CVD REQUIRED MODULE)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE ${CVD_LIBRARIES})
target_include_directories(${PROJECT_NAME} PRIVATE ${CVD_INCLUDE_DIRS})
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
