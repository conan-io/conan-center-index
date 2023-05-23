cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

find_package(zmarok-semver CONFIG REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE zmarok-semver::zmarok-semver)
set_target_properties(${PROJECT_NAME} PROPERTIES CXX_STANDARD 14)
