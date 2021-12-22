cmake_minimum_required(VERSION 3.0)
project(gsoap_example CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(gsoap REQUIRED)

add_executable(${PROJECT_NAME} 
    example.cpp
    ${CMAKE_BINARY_DIR}/soapC.cpp
    ${CMAKE_BINARY_DIR}/soapcalcProxy.cpp
)
target_include_directories(${PROJECT_NAME} PRIVATE ${CMAKE_BINARY_DIR})
target_link_libraries(${PROJECT_NAME} gsoap::gsoap)
