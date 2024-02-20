cmake_minimum_required(VERSION 3.15)
project(test_package)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(limereport REQUIRED)

if(QT_VERSION VERSION_GREATER_EQUAL "6.0.0")
    find_package(Qt6 COMPONENTS Core Widgets REQUIRED CONFIG)
elseif(QT_VERSION VERSION_GREATER_EQUAL "5.0.0")
    find_package(Qt5 COMPONENTS Core Widgets REQUIRED CONFIG)
else()
    message(FATAL_ERROR "Qt < 5 not yet supported in this recipe")
endif()

add_executable(${PROJECT_NAME} test_package.cpp)

target_link_libraries(${PROJECT_NAME}
    Qt${QT_VERSION_MAJOR}::Core
    Qt${QT_VERSION_MAJOR}::Widgets
    Qt${QT_VERSION_MAJOR}::PrintSupport
    Qt${QT_VERSION_MAJOR}::Qml
    Qt${QT_VERSION_MAJOR}::Sql limereport::limereport)