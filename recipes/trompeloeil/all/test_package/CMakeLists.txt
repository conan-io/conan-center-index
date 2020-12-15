project(test_package CXX)
cmake_minimum_required(VERSION 3.5)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_executable(${PROJECT_NAME} example.cpp)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 14)
conan_target_link_libraries(${PROJECT_NAME})
