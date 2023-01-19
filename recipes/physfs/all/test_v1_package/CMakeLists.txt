cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(PhysFS REQUIRED CONFIG)

add_executable(${PROJECT_NAME} ../test_package/test_package.c)
if(TARGET physfs-static)
    target_link_libraries(${PROJECT_NAME} PRIVATE physfs-static)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE physfs)
endif()
