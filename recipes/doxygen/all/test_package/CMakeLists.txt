cmake_minimum_required(VERSION 3.3)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)

find_package(Doxygen REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)

doxygen_add_docs(docs test_package.cpp ALL COMMENT "generate HTML")
