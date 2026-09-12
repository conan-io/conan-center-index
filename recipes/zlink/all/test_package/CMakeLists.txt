cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(zlink REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
if(ZLINK_SHARED)
  target_link_libraries(${PROJECT_NAME} PRIVATE libzlink)
else()
  target_link_libraries(${PROJECT_NAME} PRIVATE libzlink-static)
endif()
