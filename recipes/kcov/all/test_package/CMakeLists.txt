cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(${PROJECT_NAME} test_package.cpp)
target_compile_definitions(${PROJECT_NAME}
                           PRIVATE BUILD_DIR="${CMAKE_CURRENT_BINARY_DIR}")
