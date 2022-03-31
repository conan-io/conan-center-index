cmake_minimum_required(VERSION 3.18)

project(example CXX)

set(CMAKE_CXX_COMPILER_VERSION 8)

add_compile_options(-std=c++2a)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(example example.cpp)

target_link_libraries(${PROJECT_NAME} stdc++fs)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
