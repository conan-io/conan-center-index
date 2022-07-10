cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(glbinding REQUIRED CONFIG)
find_package(glfw3 REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} glbinding::glbinding glfw)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
