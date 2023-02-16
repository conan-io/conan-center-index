cmake_minimum_required(VERSION 3.1)

project(test_package C)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)

conan_basic_setup(TARGETS)

find_package(tinycthread REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.c)
target_link_libraries(${PROJECT_NAME} tinycthread::tinycthread)
target_compile_features(${PROJECT_NAME} PRIVATE c_std_11)
