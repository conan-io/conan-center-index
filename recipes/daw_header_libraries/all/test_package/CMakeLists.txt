cmake_minimum_required(VERSION 3.8)

project(test_package CXX)

find_package(daw-header-libraries CONFIG REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} daw::daw-header-libraries)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
