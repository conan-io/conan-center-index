cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(spdlog REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
if(SPDLOG_HEADER_ONLY)
    target_link_libraries(${PROJECT_NAME} PUBLIC spdlog::spdlog_header_only)
else()
    target_link_libraries(${PROJECT_NAME} PUBLIC spdlog::spdlog)
endif()
set_target_properties(${PROJECT_NAME} PROPERTIES CXX_STANDARD 11)
