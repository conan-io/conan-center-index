cmake_minimum_required(VERSION 3.1)
project(test_package)

find_package(imutils_cpp REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} imutils_cpp::imutils_cpp)
