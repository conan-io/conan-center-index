cmake_minimum_required(VERSION 3.8)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(libavrocpp REQUIRED CONFIG)
add_executable(${PROJECT_NAME} test_package.cpp)

set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)

if(TARGET libavrocpp::avrocpp)
    target_link_libraries(${PROJECT_NAME} libavrocpp::avrocpp)
else()
    target_link_libraries(${PROJECT_NAME} libavrocpp::avrocpp_s)
endif()
