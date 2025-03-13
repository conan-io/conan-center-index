cmake_minimum_required(VERSION 3.15)
project(test_package)

find_package(OpenBLAS CONFIG)
find_package(OpenBLAS64 CONFIG)
if(NOT OpenBLAS_FOUND AND NOT OpenBLAS64_FOUND)
    message(FATAL_ERROR "OpenBLAS not found")
endif()

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} OpenBLAS::OpenBLAS)
