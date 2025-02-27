cmake_minimum_required(VERSION 3.8)

project(test_package LANGUAGES CXX)

find_package(daw-header-libraries REQUIRED CONFIG)

if(daw-header-libraries_VERSION VERSION_LESS "2.109.0")
    add_executable(${PROJECT_NAME} test_package_old.cpp)
else()
    add_executable(${PROJECT_NAME} test_package.cpp)
endif()
target_link_libraries(${PROJECT_NAME} PRIVATE daw::daw-header-libraries)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
