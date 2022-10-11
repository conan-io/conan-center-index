cmake_minimum_required(VERSION 3.18)

project(RuntimeQml LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)

set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)

find_package(Qt6 CONFIG REQUIRED)

set(CODE_FILES
    runtimeqml.cpp
)

set(HEADER_FILES
    runtimeqml.hpp
)

add_library(RuntimeQml ${CODE_FILES} ${HEADER_FILES})
target_link_libraries(RuntimeQml PRIVATE qt::qt)
set_target_properties(RuntimeQml PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin/$<0:>)
set_target_properties(RuntimeQml PROPERTIES ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib/$<0:>)
set_target_properties(RuntimeQml PROPERTIES LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/lib/$<0:>)
target_include_directories(RuntimeQml PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
