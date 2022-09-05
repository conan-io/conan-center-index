cmake_minimum_required(VERSION 3.1)
project(test_package LANGUAGES C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(mongoc-1.0 REQUIRED CONFIG)

add_executable(${PROJECT_NAME} ../test_package/test_package.c)
if(TARGET mongo::mongoc_shared)
    target_link_libraries(${PROJECT_NAME} PRIVATE mongo::mongoc_shared mongo::bson_shared)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE mongo::mongoc_static mongo::bson_static)
endif()
