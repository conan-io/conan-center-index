cmake_minimum_required(VERSION 3.1)
project(test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)

conan_basic_setup(TARGETS)

find_package(flecs REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
if(FLECS_SHARED)
  target_link_libraries(${PROJECT_NAME} flecs::flecs)
else()
  target_link_libraries(${PROJECT_NAME} flecs::flecs_static)
endif()
