cmake_minimum_required(VERSION 3.6)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGET)

find_package(glibmm REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)

if (TARGET glibmm::glibmm-2.68)
  set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 17)
  target_link_libraries(${PROJECT_NAME} glibmm::glibmm-2.68 glibmm::giomm-2.68)
else()
  set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
  target_link_libraries(${PROJECT_NAME} glibmm::glibmm-2.4 glibmm::giomm-2.4)
endif()

