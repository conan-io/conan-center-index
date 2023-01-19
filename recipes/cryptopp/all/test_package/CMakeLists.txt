cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES CXX)

find_package(cryptopp REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
if(TARGET cryptopp-shared)
    target_link_libraries(${PROJECT_NAME} PRIVATE cryptopp-shared)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE cryptopp-static)
endif()
