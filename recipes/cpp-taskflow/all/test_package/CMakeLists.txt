cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(cpp-taskflow REQUIRED CONFIG)

set(CPPTASKFLOW_CXX_STANDARD 14)
if (cpp-taskflow_VERSION LESS_EQUAL "2.2.0")
    set(CPPTASKFLOW_CXX_STANDARD 17)
endif()

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE cpp-taskflow::cpp-taskflow)
set_target_properties(${PROJECT_NAME} PROPERTIES CXX_STANDARD ${CPPTASKFLOW_CXX_STANDARD})
