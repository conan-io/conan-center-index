cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(cppitertools REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} cppitertools::cppitertools)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 17)

if(ZIP_LONGEST)
    add_executable(test_zip_longest test_zip_longest.cpp)
    target_link_libraries(test_zip_longest cppitertools::cppitertools)
    set_property(TARGET test_zip_longest PROPERTY CXX_STANDARD 17)
endif()
