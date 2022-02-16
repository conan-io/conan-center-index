cmake_minimum_required(VERSION 3.15.0 FATAL_ERROR)
project(opene57_example CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(opene57 REQUIRED CONFIG)

add_executable(${PROJECT_NAME} example.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE opene57::opene57)
set_target_properties(${PROJECT_NAME} PROPERTIES CXX_STANDARD 17)
