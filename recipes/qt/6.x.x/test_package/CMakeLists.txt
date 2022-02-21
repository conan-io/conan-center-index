cmake_minimum_required(VERSION 3.3.0)

project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_set_vs_runtime()
conan_set_libcxx()
conan_output_dirs_setup()

find_package(Qt6 COMPONENTS Core Network Sql Concurrent Xml REQUIRED CONFIG)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)

add_executable(${PROJECT_NAME} test_package.cpp greeter.h example.qrc)

set_property(TARGET ${PROJECT_NAME} PROPERTY CXX_STANDARD 17)

target_link_libraries(${PROJECT_NAME} Qt6::Core Qt6::Network Qt6::Sql Qt6::Concurrent Qt6::Xml)

# check if extra qt cmake functions are usable
qt_add_executable(${PROJECT_NAME}2 test_package.cpp greeter.h example.qrc)

set_property(TARGET ${PROJECT_NAME}2 PROPERTY CXX_STANDARD 17)

target_link_libraries(${PROJECT_NAME}2 PRIVATE Qt6::Core Qt6::Network Qt6::Sql Qt6::Concurrent Qt6::Xml)
