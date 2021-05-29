cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(OpenVDB REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 14)

if(TARGET OpenVDB::openvdb_static)
  target_link_libraries(${PROJECT_NAME} PRIVATE OpenVDB::openvdb_static)
else()
  target_link_libraries(${PROJECT_NAME} PRIVATE OpenVDB::openvdb_shared)
endif()
