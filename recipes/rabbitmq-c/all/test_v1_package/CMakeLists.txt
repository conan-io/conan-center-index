cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(rabbitmq-c REQUIRED CONFIG)

add_executable(${PROJECT_NAME} ../test_package/test_package.cpp)
if(RABBITMQ_SHARED)
    target_link_libraries(${PROJECT_NAME} PRIVATE rabbitmq::rabbitmq)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE rabbitmq::rabbitmq-static)
endif()

if(WITH_SSL)
    target_compile_definitions(${PROJECT_NAME} PRIVATE WITH_SSL)
endif()
