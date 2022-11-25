cmake_minimum_required(VERSION 3.8)

project(test_package CXX)

find_package(unordered_dense REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE unordered_dense::unordered_dense)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
