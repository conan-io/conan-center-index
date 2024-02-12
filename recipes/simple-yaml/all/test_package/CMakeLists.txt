cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(simple-yaml REQUIRED CONFIG)

add_executable(${PROJECT_NAME} src/test.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE simple-yaml::simple-yaml)

set_target_properties(${PROJECT_NAME}
    PROPERTIES
    	CXX_STANDARD 20
    	CXX_STANDARD_REQUIRED ON
    	CXX_EXTENSIONS OFF
)
