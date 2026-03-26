cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(QT NAMES Qt6 Qt5 REQUIRED COMPONENTS Core Gui Widgets)
find_package(Qt${QT_VERSION_MAJOR} REQUIRED COMPONENTS Core Gui Widgets)
find_package(qt${QT_VERSION_MAJOR}advanceddocking REQUIRED CONFIG)
add_executable(example example.cpp)
target_link_libraries(example ads::qt${QT_VERSION_MAJOR}advanceddocking Qt${QT_VERSION_MAJOR}::Core Qt${QT_VERSION_MAJOR}::Gui Qt${QT_VERSION_MAJOR}::Widgets)
