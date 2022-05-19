cmake_minimum_required(VERSION 3.12)
project(test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(PhysFS REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
if(TARGET physfs-static)
    target_link_libraries(${PROJECT_NAME} physfs-static)
else()
    target_link_libraries(${PROJECT_NAME} physfs)
endif()
