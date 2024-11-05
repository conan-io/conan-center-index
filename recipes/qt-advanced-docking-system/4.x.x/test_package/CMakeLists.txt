cmake_minimum_required(VERSION 3.15)

project(ads_example_simple)
find_package(QT NAMES Qt6 Qt5 COMPONENTS Core REQUIRED)
find_package(Qt${QT_VERSION_MAJOR} 5.5 COMPONENTS Core Gui Widgets REQUIRED)
find_package(qt-advanced-docking-system CONFIG REQUIRED)
set(CMAKE_INCLUDE_CURRENT_DIR ON)
add_executable(SimpleExample WIN32
    src/main.cpp
    src/MainWindow.cpp
    src/MainWindow.ui
)
#target_include_directories(SimpleExample PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/../../src")
#target_link_libraries(SimpleExample PUBLIC qt${QT_VERSION_MAJOR}advanceddocking)
target_link_libraries(SimpleExample PUBLIC qt-advanced-docking-system::qt-advanced-docking-system)
target_link_libraries(SimpleExample PUBLIC Qt${QT_VERSION_MAJOR}::Core
                                           Qt${QT_VERSION_MAJOR}::Gui
                                           Qt${QT_VERSION_MAJOR}::Widgets
                                           xcb)
set_target_properties(SimpleExample PROPERTIES
    AUTOMOC ON
    AUTORCC ON
    AUTOUIC ON
    CXX_STANDARD 14
    CXX_STANDARD_REQUIRED ON
    CXX_EXTENSIONS OFF
    EXPORT_NAME "Qt Advanced Docking System Simple Example"
    ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/${ads_PlatformDir}/lib"
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/${ads_PlatformDir}/lib"
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/${ads_PlatformDir}/bin"
)
