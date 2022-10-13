cmake_minimum_required(VERSION 3.8)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(range-v3 REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} range-v3::range-v3)
if(MSVC AND ${VERSION} STREQUAL "0.10.0")
  set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 20)
else()
  set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 17)
endif()
