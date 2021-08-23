cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_executable(${PROJECT_NAME} test_package.cpp)

find_package(e57format REQUIRED CONFIG)
target_link_libraries(${PROJECT_NAME} PRIVATE E57Format)
set_target_properties(${PROJECT_NAME} PROPERTIES CXX_STANDARD 11)
