cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(octomap REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
if(OCTOMAP_SHARED)
  target_link_libraries(${PROJECT_NAME} octomap octomath)
else()
  target_link_libraries(${PROJECT_NAME} octomap-static octomath-static)
endif()
