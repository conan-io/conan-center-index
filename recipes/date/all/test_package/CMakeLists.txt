cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(date REQUIRED)

add_executable(${PROJECT_NAME} src/test_package.cpp)
target_link_libraries(${PROJECT_NAME} date::date)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
if(DATE_HEADER_ONLY)
  target_compile_definitions(${PROJECT_NAME} PRIVATE DATE_HEADER_ONLY)
endif()
