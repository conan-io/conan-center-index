cmake_minimum_required(VERSION 3.1)
project(test_package CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(spdlog REQUIRED CONFIG)

add_executable(${PROJECT_NAME} ../test_package/test_package.cpp)
if(TARGET spdlog::spdlog_header_only)
    target_link_libraries(${PROJECT_NAME} spdlog::spdlog_header_only)
else()
    target_link_libraries(${PROJECT_NAME} spdlog::spdlog)
endif()
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
