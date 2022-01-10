cmake_minimum_required(VERSION 3.15)
project(test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(GKlib REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test.c)
target_link_libraries(${PROJECT_NAME} GKlib::GKlib)
