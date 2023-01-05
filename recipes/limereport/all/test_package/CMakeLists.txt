cmake_minimum_required(VERSION 3.1)
project(test_package)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(limereport REQUIRED)


add_executable(${PROJECT_NAME} test_package.cpp)

target_link_libraries(${PROJECT_NAME} limereport::limereport)
