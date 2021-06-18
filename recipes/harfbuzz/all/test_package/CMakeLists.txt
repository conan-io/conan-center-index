cmake_minimum_required(VERSION 3.1)
project(test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

file(COPY ${CMAKE_CURRENT_SOURCE_DIR}/example.ttf
     DESTINATION ${CMAKE_CURRENT_BINARY_DIR})

find_package(harfbuzz REQUIRED CONFIG)

add_executable(${PROJECT_NAME} example.c)
target_link_libraries(${PROJECT_NAME} harfbuzz::harfbuzz)
set_property(TARGET ${PROJECT_NAME} PROPERTY C_STANDARD 99)
