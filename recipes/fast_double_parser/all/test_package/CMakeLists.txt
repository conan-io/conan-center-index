cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(fast_double_parser REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} fast_double_parser::fast_double_parser)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
