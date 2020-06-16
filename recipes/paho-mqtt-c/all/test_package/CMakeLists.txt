cmake_minimum_required(VERSION 2.8.11)
project(test_package C)

set(CMAKE_VERBOSE_MAKEFILE TRUE)

option(BUILD_ASYNC "Build asynchronous example" ON)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

if (BUILD_ASYNC)
    add_executable(${PROJECT_NAME} test_package_async.c)
else()
    add_executable(${PROJECT_NAME} test_package_client.c)
endif()
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
