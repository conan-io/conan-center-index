cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(source_location REQUIRED CONFIG)

add_executable(${PROJECT_NAME} src/test.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE source_location::source_location)
set_target_properties(${PROJECT_NAME}
    PROPERTIES
    	CXX_STANDARD 11
    	CXX_STANDARD_REQUIRED ON
    	CXX_EXTENSIONS OFF
)
