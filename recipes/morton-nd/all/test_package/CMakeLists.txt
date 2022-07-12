cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(morton-nd REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} morton-nd::MortonND)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 14)
if(morton-nd_VERSION VERSION_LESS "4.0.0")
    target_compile_definitions(${PROJECT_NAME} PRIVATE "MORTONND_LESS_4_0_0")
endif()
