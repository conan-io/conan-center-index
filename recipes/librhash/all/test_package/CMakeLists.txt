cmake_minimum_required(VERSION 3.3)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()
set(CMAKE_CXX_STANDARD 11)

add_executable(${PROJECT_NAME} example.cpp)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
