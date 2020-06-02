cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_executable(${PROJECT_NAME} example.cpp DeserializerTest.cpp)
target_link_libraries(${PROJECT_NAME} CONAN_PKG::oatpp)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
