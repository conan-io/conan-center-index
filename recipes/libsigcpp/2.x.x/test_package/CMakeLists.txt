cmake_minimum_required(VERSION 3.6)
project(test_package)

find_package(PkgConfig REQUIRED)
pkg_search_module(SIGCPP IMPORTED_TARGET REQUIRED sigc++-2.0)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE PkgConfig::SIGCPP)
set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 11)
