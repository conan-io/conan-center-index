cmake_minimum_required(VERSION 3.15)
# Specify the C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

project(PackageTest CXX)

find_package(mysql-connector-cpp REQUIRED CONFIG)

add_executable(${PROJECT_NAME} src/example.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE mysql::concpp)
