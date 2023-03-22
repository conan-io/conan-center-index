cmake_minimum_required(VERSION 3.25)

project(test_package CXX) # if the project uses c++

find_package(essentials REQUIRED CONFIG)

include_directories(${essentials_INCLUDE_DIRS})
add_executable(${PROJECT_NAME} test_package.cpp)

target_link_libraries(${PROJECT_NAME} PRIVATE essentials::essentials)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
