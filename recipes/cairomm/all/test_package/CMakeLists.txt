cmake_minimum_required(VERSION 3.6)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGET)

add_executable(${PROJECT_NAME} test_package.cpp)

find_package(cairomm REQUIRED CONFIG)
if (TARGET cairomm::cairomm-1.16)
  set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 17)
  target_link_libraries(${PROJECT_NAME} cairomm::cairomm-1.16)
else()
  set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
  target_link_libraries(${PROJECT_NAME} cairomm::cairomm-1.0)
endif()
