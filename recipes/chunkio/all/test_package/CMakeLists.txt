cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C)

find_package(chunkio REQUIRED CONFIG)

if(chunkio_VERSION VERSION_LESS "1.5.0")
    add_executable(${PROJECT_NAME} test_package.c)
else()
    add_executable(${PROJECT_NAME} test_package_1_5_0.c)
endif()
target_link_libraries(${PROJECT_NAME} PRIVATE chunkio::chunkio)
