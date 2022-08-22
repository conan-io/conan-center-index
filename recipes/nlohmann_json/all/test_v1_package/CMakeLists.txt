cmake_minimum_required(VERSION 3.1.2)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(nlohmann_json REQUIRED CONFIG)

add_executable(${PROJECT_NAME} ../test_package/test_package.cpp)
target_link_libraries(${PROJECT_NAME} nlohmann_json::nlohmann_json)
set_target_properties(${PROJECT_NAME} PROPERTIES CXX_STANDARD 11)
