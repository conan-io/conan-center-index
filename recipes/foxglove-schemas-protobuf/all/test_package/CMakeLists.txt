cmake_minimum_required(VERSION 3.8)
project(test_package CXX)

find_package(foxglove-schemas-protobuf CONFIG REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} foxglove-schemas-protobuf::foxglove-schemas-protobuf)
set_target_properties(${PROJECT_NAME} PROPERTIES CXX_STANDARD 17 CXX_STANDARD_REQUIRED ON)
