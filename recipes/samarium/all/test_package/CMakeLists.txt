cmake_minimum_required(VERSION 3.16)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)
# find_package(samarium REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} CONAN_PKG::samarium)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 20)
