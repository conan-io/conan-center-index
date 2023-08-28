cmake_minimum_required(VERSION 3.15)

project(test_package CXX)

find_package(ohnet REQUIRED COMPONENTS ohNetCore ohNetProxies TestFramework)

set(CMAKE_CXX_FLAGS "-DDEFINE_LITTLE_ENDIAN")

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE ohNetCore TestFramework)
