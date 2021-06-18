cmake_minimum_required(VERSION 3.8)
project(test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(s2let REQUIRED NO_MODULE)

add_executable(${PROJECT_NAME} example.c)
target_compile_features(${PROJECT_NAME} PUBLIC c_std_99)
target_link_libraries(${PROJECT_NAME} s2let::s2let)
