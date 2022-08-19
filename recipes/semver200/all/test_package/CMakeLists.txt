cmake_minimum_required(VERSION 3.11)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(semver200 CONFIG REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} semver200::semver200)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 14)
