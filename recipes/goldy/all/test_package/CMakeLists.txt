cmake_minimum_required(VERSION 3.15)
project(test_goldy LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(goldy REQUIRED CONFIG)

add_executable(test_goldy test_goldy.cpp)
target_link_libraries(test_goldy PRIVATE goldy::goldy)

