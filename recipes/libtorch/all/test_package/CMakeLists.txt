cmake_minimum_required(VERSION 3.15)

project(test_package LANGUAGES CXX C)

find_package(Torch REQUIRED CONFIG)

#https://pytorch.org/cppdocs/installing.html
add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE ${TORCH_LIBRARIES})
