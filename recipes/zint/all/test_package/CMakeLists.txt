cmake_minimum_required(VERSION 3.1)
project(test_package)

find_package(zint REQUIRED)

set(CMAKE_POSITION_INDEPENDENT_CODE ON)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} zint::zint)


