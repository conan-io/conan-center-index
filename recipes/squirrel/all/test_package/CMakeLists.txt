cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(squirrel REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
if(SQUIRREL_SHARED)
  target_link_libraries(${PROJECT_NAME} squirrel::squirrel squirrel::sqstdlib)
else()
  target_link_libraries(${PROJECT_NAME} squirrel::squirrel_static squirrel::sqstdlib_static)
endif()
