cmake_minimum_required(VERSION 3.1)
project(PackageTest CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(glew CONFIG REQUIRED)
find_package(glshaderpp CONFIG REQUIRED)

add_executable(${PROJECT_NAME} example.cpp)
target_link_libraries(${PROJECT_NAME} glshaderpp::glshaderpp GLEW::GLEW)
set_target_properties(${PROJECT_NAME} PROPERTIES CXX_STANDARD 17 CXX_STANDARD_REQUIRED ON)
