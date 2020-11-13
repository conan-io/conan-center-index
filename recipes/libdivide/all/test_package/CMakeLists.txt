cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(libdivide REQUIRED CONFIG)

add_executable(${PROJECT_NAME}_c test_package.c)
target_link_libraries(${PROJECT_NAME}_c libdivide::libdivide)
set_property(TARGET ${PROJECT_NAME}_c PROPERTY C_STANDARD 99)

add_executable(${PROJECT_NAME}_cpp test_package.cpp)
target_link_libraries(${PROJECT_NAME}_cpp libdivide::libdivide)
set_property(TARGET ${PROJECT_NAME}_cpp PROPERTY CXX_STANDARD 11)
