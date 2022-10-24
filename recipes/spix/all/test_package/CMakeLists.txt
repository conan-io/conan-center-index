cmake_minimum_required(VERSION 3.8)

project(test_spix CXX)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(spix REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_spix.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE spix::spix)
