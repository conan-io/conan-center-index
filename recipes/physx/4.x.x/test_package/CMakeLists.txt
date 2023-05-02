cmake_minimum_required(VERSION 3.1)
project(test_package)

find_package(PhysX REQUIRED PhysX PhysXExtensions CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PhysX::PhysX PhysX::PhysXExtensions)

option(TEST_SHARED_LIBRARY "Build a test shared library")
if(TEST_SHARED_LIBRARY)
    find_package(PhysX REQUIRED PhysXFoundation CONFIG)
    add_library(${PROJECT_NAME}_lib SHARED test_library.cpp)
    target_link_libraries(${PROJECT_NAME}_lib PhysX::PhysXFoundation PhysX::PhysXExtensions)
endif()