cmake_minimum_required(VERSION 2.8.11)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(Iconv)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} Iconv::Iconv)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
