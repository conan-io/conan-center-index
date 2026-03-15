cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)


find_package(msgpack23 REQUIRED CONFIG)

if (IS_NEW_API)
add_executable(${PROJECT_NAME} test_package_new.cpp)
else()
add_executable(${PROJECT_NAME} test_package_old.cpp)
endif()
target_link_libraries(${PROJECT_NAME} PRIVATE msgpack23::msgpack23)
