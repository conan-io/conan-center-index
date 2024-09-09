cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(ctpg CONFIG REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} ctpg::ctpg)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 17)

if("${CMAKE_CXX_COMPILER_ID}" STREQUAL "MSVC")
    target_compile_options(${PROJECT_NAME} PUBLIC -constexpr:depth3000000)
    target_compile_options(${PROJECT_NAME} PUBLIC -constexpr:steps3000000)
endif()
