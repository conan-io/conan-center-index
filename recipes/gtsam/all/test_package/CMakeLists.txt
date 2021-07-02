cmake_minimum_required(VERSION 3.0)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(${PROJECT_NAME} test_package.cpp)

find_package(GTSAM REQUIRED)
target_link_libraries(${PROJECT_NAME} GTSAM::gtsam)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
