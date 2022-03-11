cmake_minimum_required(VERSION 3.8)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(rmlui REQUIRED CONFIG)

add_executable(${PROJECT_NAME} example.cpp)
target_compile_Features(${PROJECT_NAME} PRIVATE cxx_std_14)
target_link_libraries(${PROJECT_NAME} rmlui::rmlui)
