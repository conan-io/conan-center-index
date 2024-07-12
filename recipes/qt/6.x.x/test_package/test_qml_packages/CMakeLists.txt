cmake_minimum_required(VERSION 3.14)

project(CheckQMLModules LANGUAGES CXX)

set(CMAKE_AUTOUIC ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(QT NAMES Qt6 Qt5 REQUIRED COMPONENTS Core Qml)
find_package(Qt6 REQUIRED COMPONENTS Core Qml)

add_executable(CheckQMLModules
  test_qml_modules.cpp
)
target_link_libraries(CheckQMLModules Qt6::Core Qt6::Qml)

include(GNUInstallDirs)
install(TARGETS CheckQMLModules
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
