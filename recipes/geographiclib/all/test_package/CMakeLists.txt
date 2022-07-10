cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(geographiclib CONFIG REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} GeographicLib::GeographicLib)

if(geographiclib_VERSION VERSION_GREATER_EQUAL "1.51")
  set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
endif()
