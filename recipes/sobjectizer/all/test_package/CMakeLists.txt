cmake_minimum_required(VERSION 3.8)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(sobjectizer REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
if(TARGET sobjectizer::SharedLib)
    target_link_libraries(${PROJECT_NAME} sobjectizer::SharedLib)
else()
    target_link_libraries(${PROJECT_NAME} sobjectizer::StaticLib)
endif()
