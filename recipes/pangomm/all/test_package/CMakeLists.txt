cmake_minimum_required(VERSION 3.6)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGET)

find_package(pangomm REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)

if (TARGET pangomm::pangomm-2.48)
  set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 17)
  target_link_libraries(${PROJECT_NAME} pangomm::pangomm-2.48)
else()
  set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
  target_link_libraries(${PROJECT_NAME} pangomm::pangomm-1.4)
endif()

