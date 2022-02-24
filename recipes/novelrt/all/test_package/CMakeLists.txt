cmake_minimum_required(VERSION 3.12)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(novelrt REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test.cpp)
target_link_libraries(${PROJECT_NAME} novelrt::novelrt)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 17)
