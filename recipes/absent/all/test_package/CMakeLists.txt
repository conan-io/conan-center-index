cmake_minimum_required(VERSION 3.10)

project(test_package LANGUAGES CXX)

set(CMAKE_MODULE_PATH ${CMAKE_BINARY_DIR})

find_package(absent REQUIRED)

add_executable(${PROJECT_NAME} main.cpp)

target_compile_features(${PROJECT_NAME}
    PRIVATE
        cxx_std_17
)

target_link_libraries(${PROJECT_NAME}
    PRIVATE
        absent::absent
)
