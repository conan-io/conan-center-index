cmake_minimum_required(VERSION 3.10)

project(test_package LANGUAGES CXX)

if(NOT EXISTS ${CMAKE_CURRENT_BINARY_DIR}/conanbuildinfo.cmake)
  message(FATAL_ERROR "Please run conan install!")
endif()

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_library(conan-hippomocks INTERFACE ${CONAN_LIBS})
add_library(Hippomocks::Hippomocks ALIAS conan-hippomocks)

add_executable(${PROJECT_NAME} main.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE Hippomocks::Hippomocks)

enable_testing()

add_test(NAME ${PROJECT_NAME} COMMAND ${PROJECT_NAME})
