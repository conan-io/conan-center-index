cmake_minimum_required(VERSION 3.8)

project(test_anyrpc CXX)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(anyrpc REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_anyrpc.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE anyrpc::anyrpc)
