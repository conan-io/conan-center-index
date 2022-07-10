cmake_minimum_required(VERSION 3.1)
project(test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(wslay REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
if(TARGET wslay_shared)
    target_link_libraries(${PROJECT_NAME} wslay_shared)
else()
    target_link_libraries(${PROJECT_NAME} wslay)
endif()
