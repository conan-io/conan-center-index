cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(jsonnet CONFIG REQUIRED)

add_executable(${PROJECT_NAME}_c test_package.c)
target_link_libraries(${PROJECT_NAME}_c jsonnet::libjsonnet)

add_executable(${PROJECT_NAME}_cxx test_package.cpp)
target_link_libraries(${PROJECT_NAME}_cxx jsonnet::libjsonnetpp)
set_property(TARGET ${PROJECT_NAME}_cxx PROPERTY CXX_STANDARD 11)
