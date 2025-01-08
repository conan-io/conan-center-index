cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

find_package(SQLite3 REQUIRED)

if(NOT SQLite3_INCLUDE_DIRS)
  message(FATAL_ERROR "SQLite3_INCLUDE_DIRS CMake variable expected, but not defined")
endif()

if(NOT SQLite3_LIBRARIES)
  message(FATAL_ERROR "SQLite3_LIBRARIES CMake variable expected, but not defined")
endif()

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE SQLite::SQLite3)

