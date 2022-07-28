cmake_minimum_required(VERSION 3.8)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(platform.ranges CONFIG REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} platform.ranges::platform.ranges)
set_target_properties(${PROJECT_NAME} PROPERTIES CXX_STANDARD 20)
