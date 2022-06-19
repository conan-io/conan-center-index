cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(tomlplusplus REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} tomlplusplus::tomlplusplus)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 17)

if(NOT DEFINED TOMLPP_BUILD_SINGLE_ONLY)
    add_executable(${PROJECT_NAME}_multi test_package_multi.cpp)
    target_link_libraries(${PROJECT_NAME}_multi tomlplusplus::tomlplusplus)
    set_property(TARGET ${PROJECT_NAME}_multi PROPERTY CXX_STANDARD 17)
endif()
