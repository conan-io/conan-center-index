cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

find_package(incbin CONFIG REQUIRED)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} incbin::incbin)
target_compile_definitions(${PROJECT_NAME} PUBLIC INCBIN_FILE="${CMAKE_SOURCE_DIR}/CMakeLists.txt")
