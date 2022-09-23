cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

option(USE_EMPTY_VFS "Using empty SQLite OS interface")

find_package(SQLite3 REQUIRED)

add_executable(${PROJECT_NAME} ../test_package/test_package.c)
target_link_libraries(${PROJECT_NAME} PRIVATE SQLite::SQLite3)

if(USE_EMPTY_VFS)
    target_compile_definitions(${PROJECT_NAME} PRIVATE USE_EMPTY_VFS)
    target_sources(${PROJECT_NAME} PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/../test_package/empty_vfs.c)
endif()
