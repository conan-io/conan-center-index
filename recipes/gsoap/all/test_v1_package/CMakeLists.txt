cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(gsoap REQUIRED CONFIG)

add_executable(${PROJECT_NAME}
    ../test_package/test_package.cpp
    ${CMAKE_BINARY_DIR}/soapC.cpp
    ${CMAKE_BINARY_DIR}/soapcalcProxy.cpp
)
target_include_directories(${PROJECT_NAME} PRIVATE ${CMAKE_BINARY_DIR})
target_link_libraries(${PROJECT_NAME} PRIVATE gsoap::gsoap)
