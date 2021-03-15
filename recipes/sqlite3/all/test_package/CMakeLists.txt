cmake_minimum_required(VERSION 3.1)
project(test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(SQLite3 REQUIRED)
message(STATUS "SQLite3_INCLUDE_DIRS: ${SQLite3_INCLUDE_DIRS}")
message(STATUS "SQLite3_LIBRARIES: ${SQLite3_LIBRARIES}")
message(STATUS "SQLite3_VERSION: ${SQLite3_VERSION}")
message(STATUS "SQLite3_FOUND: ${SQLite3_FOUND}")

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} SQLite::SQLite3)
