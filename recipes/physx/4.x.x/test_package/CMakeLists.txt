cmake_minimum_required(VERSION 2.8.12)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})

option(TEST_SHARED_LIBRARY "Build a test shared library")
if(TEST_SHARED_LIBRARY)
    add_library(${PROJECT_NAME}_lib SHARED test_library.cpp)
    target_link_libraries(${PROJECT_NAME}_lib ${CONAN_LIBS})
endif()
