cmake_minimum_required(VERSION 3.8)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(Taskflow REQUIRED CONFIG)

set(_CXX_STANDARD cxx_std_14)
if (Taskflow_VERSION GREATER_EQUAL "3.0.0")
    set(_CXX_STANDARD cxx_std_17)
endif()

add_executable(${PROJECT_NAME} test_package.cpp)
target_compile_features(${PROJECT_NAME} PRIVATE ${_CXX_STANDARD})
target_link_libraries(${PROJECT_NAME} Taskflow::Taskflow)
