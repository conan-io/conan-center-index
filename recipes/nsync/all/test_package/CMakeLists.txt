cmake_minimum_required(VERSION 3.1)
project(test_package C CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(nsync CONFIG REQUIRED)

add_executable(${PROJECT_NAME} example_c.c)
target_link_libraries(${PROJECT_NAME} nsync::nsync_c)

add_executable(${PROJECT_NAME}_cpp example_cpp.cpp)
target_link_libraries(${PROJECT_NAME}_cpp nsync::nsync_cpp)

