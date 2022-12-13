cmake_minimum_required(VERSION 3.8)

project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(mqtt_cpp_iface REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} mqtt_cpp_iface::mqtt_cpp_iface)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_14)
