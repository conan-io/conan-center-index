cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(minizip)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} minizip::minizip)
set_property(TARGET ${PROJECT_NAME} PROPERTY C_STANDARD 11)
