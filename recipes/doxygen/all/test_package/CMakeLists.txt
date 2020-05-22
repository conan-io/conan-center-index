cmake_minimum_required(VERSION 2.8.12)
cmake_policy(SET CMP0057 NEW) # if IN_LIST

include(${CMAKE_BINARY_DIR}/conan_paths.cmake)

project(test_package)

find_package(Doxygen REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)

doxygen_add_docs(docs test_package.cpp ALL COMMENT "generate HTML")
