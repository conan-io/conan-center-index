cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(pybind11_json REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} pybind11_json::pybind11_json)  # FIXME: target should be pybind11_json
set_target_properties(${PROJECT_NAME} PROPERTIES CXX_STANDARD 11)
