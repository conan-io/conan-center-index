cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES C CXX)

if(WITH_CXX)
    find_package(reproc++ REQUIRED CONFIG)
else()
    find_package(reproc REQUIRED CONFIG)
endif()

add_executable(${PROJECT_NAME}_c test_package.c)
target_link_libraries(${PROJECT_NAME}_c PRIVATE reproc)
target_compile_features(${PROJECT_NAME}_c PRIVATE c_std_99)

if(WITH_CXX)
    add_executable(${PROJECT_NAME}_cpp test_package.cpp)
    target_link_libraries(${PROJECT_NAME}_cpp PRIVATE reproc++)
    target_compile_features(${PROJECT_NAME}_cpp PRIVATE cxx_std_11)
endif()
