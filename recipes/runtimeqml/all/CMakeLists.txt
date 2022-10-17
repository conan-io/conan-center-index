cmake_minimum_required(VERSION 3.18)

project(runtimeqml LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)

set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)

find_package(Qt5 CONFIG)
find_package(Qt6 CONFIG)
if (Qt6_FOUND)
    add_library(${PROJECT_NAME} runtimeqml.hpp runtimeqml.cpp)
elseif(Qt5_FOUND)
    add_library(${PROJECT_NAME} runtimeqml.h runtimeqml.cpp)
else()
    message(FATAL_ERROR "Qt was not found")
endif()

target_link_libraries(${PROJECT_NAME} PRIVATE qt::qt)
set_target_properties(${PROJECT_NAME} PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin/$<0:>)
set_target_properties(${PROJECT_NAME} PROPERTIES ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib/$<0:>)
set_target_properties(${PROJECT_NAME} PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib/$<0:>)
target_include_directories(${PROJECT_NAME} PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
