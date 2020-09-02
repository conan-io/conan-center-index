cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(octomap REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
# TODO: no namespace
if(OCTOMAP_SHARED)
  target_link_libraries(${PROJECT_NAME} octomap::octomap octomap::octomath)
else()
  target_link_libraries(${PROJECT_NAME} octomap::octomap-static octomap::octomath-static)
endif()
