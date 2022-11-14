cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

find_package(nlohmann_json_schema_validator CONFIG REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
target_link_libraries(${PROJECT_NAME} nlohmann_json_schema_validator::nlohmann_json_schema_validator)
