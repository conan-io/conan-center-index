cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(allegro5 REQUIRED)

add_executable(${PROJECT_NAME} al_ex_color2.cpp)
target_link_libraries(${PROJECT_NAME} allegro5::allegro5)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
