cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(stringzilla REQUIRED CONFIG)

if (stringzilla_VERSION VERSION_LESS 2.0)
    add_executable(${PROJECT_NAME} test_package.cpp)
elseif(stringzilla_VERSION VERSION_LESS 3.0)
    add_executable(${PROJECT_NAME} test_package_2_0.cpp)
else()
    add_executable(${PROJECT_NAME} test_package_3_0.cpp)
endif()
target_link_libraries(${PROJECT_NAME} PRIVATE stringzilla::stringzilla)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
