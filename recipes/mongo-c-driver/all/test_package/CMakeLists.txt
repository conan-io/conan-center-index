cmake_minimum_required(VERSION 3.1)
project(test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(mongoc-1.0 REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
if(MONGO-C-DRIVER_SHARED)
  target_link_libraries(${PROJECT_NAME} mongo::mongoc_shared mongo::bson_shared)
else()
  target_link_libraries(${PROJECT_NAME} mongo::mongoc_static mongo::bson_static)
endif()
