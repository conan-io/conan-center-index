cmake_minimum_required(VERSION 3.1)
project(test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

option(USE_EMPTY_VFS "Using empty SQLite OS interface")

find_package(SQLite3 REQUIRED)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} SQLite::SQLite3)

if(USE_EMPTY_VFS)
    target_compile_definitions(${PROJECT_NAME} PRIVATE USE_EMPTY_VFS)
    target_sources(${PROJECT_NAME} PRIVATE empty_vfs.c)
endif()
