cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(glm REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
if (TARGET glm::glm)
    target_link_libraries(${PROJECT_NAME} PRIVATE glm::glm)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE glm::glm-header-only)
endif()
