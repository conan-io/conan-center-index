cmake_minimum_required(VERSION 3.1)

project(test_package)

find_package(cudart REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE cudart::cudart)
