cmake_minimum_required(VERSION 3.15)

project(example CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(ecfeed CONFIG REQUIRED)

add_executable(example example.cpp)
target_link_libraries(${PROJECT_NAME} ecfeed::ecfeed)
set_target_properties(${PROJECT_NAME} PROPERTIES CXX_STANDARD 20)
