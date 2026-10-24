cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(QT NAMES Qt6 Qt5 REQUIRED COMPONENTS Core Gui Widgets)
find_package(Qt${QT_VERSION_MAJOR} REQUIRED COMPONENTS Core Gui Widgets)
find_package(${ADS_CMAKE_FILE_NAME} REQUIRED CONFIG)
add_executable(example example.cpp)
target_link_libraries(example ${ADS_CMAKE_TARGET_NAME} Qt${QT_VERSION_MAJOR}::Core Qt${QT_VERSION_MAJOR}::Gui Qt${QT_VERSION_MAJOR}::Widgets)
