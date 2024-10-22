cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(Qt5 COMPONENTS Core Network Sql Concurrent Xml REQUIRED CONFIG)
find_package(Qt5 OPTIONAL_COMPONENTS Qml)

add_executable(${PROJECT_NAME} test_package.cpp greeter.h example.qrc)
target_link_libraries(${PROJECT_NAME} PRIVATE Qt5::Core Qt5::Network Qt5::Sql Qt5::Concurrent Qt5::Xml)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_11)
set_target_properties(${PROJECT_NAME} PROPERTIES AUTOMOC ON AUTORCC ON)

# check if QML modules are build and correctly deployed, if enabled
if (TARGET Qt5::Qml)
  add_executable(CheckQMLModules test_qml_modules.cpp)
  target_link_libraries(CheckQMLModules Qt5::Core Qt5::Qml)
  target_compile_features(CheckQMLModules PRIVATE cxx_std_11)
  set_target_properties(CheckQMLModules PROPERTIES AUTOMOC ON AUTORCC ON)
endif()
