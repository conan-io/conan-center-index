cmake_minimum_required(VERSION 3.3)

include(${CMAKE_BINARY_DIR}/conan_paths.cmake)

project(test_package)

find_package(Doxygen REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)

doxygen_add_docs(docs test_package.cpp ALL COMMENT "generate HTML")
