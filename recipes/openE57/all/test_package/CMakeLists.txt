cmake_minimum_required(VERSION 3.15.0 FATAL_ERROR)
project(opene57_example CXX)

set(CMAKE_MODULE_PATH ${CMAKE_BINARY_DIR} ${CMAKE_MODULE_PATH})

find_package(opene57 REQUIRED)

add_executable(${PROJECT_NAME} 
    example.cpp
)

target_include_directories(${PROJECT_NAME} PRIVATE ${opene57_INCLUDE_DIRS})
target_link_libraries(${PROJECT_NAME} PRIVATE ${opene57_LIBRARIES})

set_target_properties( ${PROJECT_NAME} 
    PROPERTIES
    ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib"
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib"
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
)
