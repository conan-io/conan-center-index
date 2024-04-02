cmake_minimum_required(VERSION 3.15)

project(test_package CXX)

find_package(asyncly REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE asyncly::asyncly)
target_compile_definitions(${PROJECT_NAME} PRIVATE WIN32_LEAN_AND_MEAN)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_20)
