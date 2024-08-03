cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(Qt6 COMPONENTS Core Network Sql Concurrent Xml REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp greeter.h example.qrc)
target_link_libraries(${PROJECT_NAME} PRIVATE Qt6::Core Qt6::Network Qt6::Sql Qt6::Concurrent Qt6::Xml Qt6::Widgets)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
set_target_properties(${PROJECT_NAME} PROPERTIES AUTOMOC ON AUTORCC ON)
