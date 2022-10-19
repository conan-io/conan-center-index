cmake_minimum_required(VERSION 3.18)

project(RuntimeQmlTest LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)

set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)

find_package(Qt6 CONFIG)
find_package(Qt5 CONFIG)
find_package(RuntimeQml CONFIG REQUIRED)

add_executable(RuntimeQmlTest main.cpp qml.qrc)
target_compile_definitions(RuntimeQmlTest PRIVATE ROOT_SOURCE_PATH="${CMAKE_CURRENT_SOURCE_DIR}")
target_link_libraries(RuntimeQmlTest PRIVATE qt::qt runtimeqml::runtimeqml)
set_target_properties(RuntimeQmlTest PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin/$<0:>)
