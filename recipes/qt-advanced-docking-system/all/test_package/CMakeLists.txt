cmake_minimum_required(VERSION 3.15)
project(test_package CXX)

find_package(QT NAMES Qt6 Qt5 REQUIRED COMPONENTS Core Gui Widgets)
find_package(Qt${QT_VERSION_MAJOR} REQUIRED COMPONENTS Core Gui Widgets)

if(ADVANCED_DOCKING_MAJOR_NEW_5)
  find_package(qtadvanceddocking-qt${QT_VERSION_MAJOR} REQUIRED CONFIG)
  set(ADS_CMAKE_TARGET_NAME ads::qtadvanceddocking-qt${QT_VERSION_MAJOR})
else()
  find_package(qt${QT_VERSION_MAJOR}advanceddocking REQUIRED CONFIG)
  set(ADS_CMAKE_TARGET_NAME ads::qt${QT_VERSION_MAJOR}advanceddocking)
endif()

add_executable(example example.cpp)
target_link_libraries(example ${ADS_CMAKE_TARGET_NAME} Qt${QT_VERSION_MAJOR}::Core Qt${QT_VERSION_MAJOR}::Gui Qt${QT_VERSION_MAJOR}::Widgets)
