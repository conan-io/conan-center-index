cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

set(CMAKE_POLICY_DEFAULT_CMP0091 NEW)

find_package(spdlog REQUIRED CONFIG)
find_package(fmt REQUIRED CONFIG)


add_executable(${PROJECT_NAME} test_package.cpp)
if(SPDLOG_HEADER_ONLY)
    target_link_libraries(${PROJECT_NAME} spdlog::spdlog_header_only fmt::fmt)
else()
    target_link_libraries(${PROJECT_NAME} spdlog::spdlog fmt::fmt)
endif()
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
