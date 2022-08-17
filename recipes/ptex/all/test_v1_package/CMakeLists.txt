cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(ptex REQUIRED CONFIG)

add_executable(${PROJECT_NAME} ../test_package/test_package.cpp)
if(TARGET Ptex::Ptex_static)
    target_link_libraries(${PROJECT_NAME} PRIVATE Ptex::Ptex_static)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE Ptex::Ptex_dynamic)
endif()
