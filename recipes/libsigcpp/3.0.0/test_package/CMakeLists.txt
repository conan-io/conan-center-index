cmake_minimum_required(VERSION 3.8)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(sigc++-3 REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} sigc++-3::sigc-3.0) # TODO: remove sigc++-3:: namespace when fixed in cpp_info of recipe
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 17)
