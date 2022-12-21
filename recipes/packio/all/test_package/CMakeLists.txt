cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)


set(CMAKE_VERBOSE_MAKEFILE ON)
find_package(packio REQUIRED CONFIG)

if (packio_VERSION VERSION_LESS "1.2.0")
    add_executable(${PROJECT_NAME} 1.0.x-1.1.x.cpp)
elseif (packio_VERSION VERSION_LESS "2.0.0")
    add_executable(${PROJECT_NAME} 1.2.x.cpp)
else ()
    add_executable(${PROJECT_NAME} latest.cpp)
endif ()

target_link_libraries(${PROJECT_NAME} PRIVATE packio::packio)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
