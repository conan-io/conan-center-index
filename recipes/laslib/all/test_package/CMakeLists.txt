cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(laslib REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)

add_custom_command(
        TARGET ${PROJECT_NAME} POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy
                ${CMAKE_CURRENT_SOURCE_DIR}/test.laz
                ${CMAKE_BINARY_DIR}/test.laz)

target_link_libraries(${PROJECT_NAME} PRIVATE laslib::laslib)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
