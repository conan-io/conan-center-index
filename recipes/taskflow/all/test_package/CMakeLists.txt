cmake_minimum_required(VERSION 2.8.12)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(Taskflow REQUIRED)

set(_CXX_STANDARD 14)
if (Taskflow_VERSION LESS_EQUAL "2.2.0")
    set(_CXX_STANDARD 17)
endif()

add_executable(${PROJECT_NAME} test_package.cpp)
set_target_properties(${PROJECT_NAME} PROPERTIES CXX_STANDARD ${_CXX_STANDARD})
target_link_libraries(${PROJECT_NAME} Taskflow::Taskflow)
