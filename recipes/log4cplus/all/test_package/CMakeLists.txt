cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

if(UNICODE)
    add_definitions("-DUNICODE")
    add_definitions("-D_UNICODE")
endif()

find_package(log4cplus REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} log4cplus::log4cplus)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
