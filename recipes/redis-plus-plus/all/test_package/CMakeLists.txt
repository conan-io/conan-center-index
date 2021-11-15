cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(redis++ REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
if(BUILDING_SHARED)
    target_link_libraries(${PROJECT_NAME} redis++::redis++)
else()
    target_link_libraries(${PROJECT_NAME} redis++::redis++_static)
endif()
