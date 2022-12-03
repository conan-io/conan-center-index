cmake_minimum_required(VERSION 3.1.2)
project(test_package CXX)

find_package(himalaya REQUIRED CONFIG)

add_executable(${PROJECT_NAME} ${PROJECT_NAME}.cpp)
target_link_libraries(${PROJECT_NAME} himalaya::himalaya)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
