cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(Flatbuffers REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
if(FLATBUFFERS_HEADER_ONLY)
  target_compile_definitions(${PROJECT_NAME} PRIVATE FLATBUFFERS_HEADER_ONLY)
endif()
if(FLATBUFFERS_SHARED)
  target_link_libraries(${PROJECT_NAME} flatbuffers::flatbuffers_shared)
else()
  target_link_libraries(${PROJECT_NAME} flatbuffers::flatbuffers)
endif()
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
