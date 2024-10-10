cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(Qt6 COMPONENTS Core Network Sql Concurrent UiTools Xml REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp greeter.h example.qrc)
target_link_libraries(${PROJECT_NAME} PRIVATE Qt6::Core Qt6::Network Qt6::Sql Qt6::Concurrent Qt6::Xml Qt6::Widgets)
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
set_target_properties(${PROJECT_NAME} PROPERTIES AUTOMOC ON AUTORCC ON)

# Only running this Qt macros in macOS
if (APPLE)
    # Related to https://github.com/conan-io/conan-center-index/issues/20574
    qt_standard_project_setup()
    qt_add_executable(test_macos_bundle MACOSX_BUNDLE test_macos_bundle.cpp)
    target_link_libraries(test_macos_bundle PRIVATE Qt6::Core)
    target_compile_features(test_macos_bundle PRIVATE cxx_std_17)
endif()

set(UI_TEST ui_test)

add_executable(${UI_TEST} test_ui.cpp test.ui)
target_link_libraries(${UI_TEST} PRIVATE Qt6::Core Qt6::Gui Qt6::UiTools Qt6::Widgets)
target_compile_features(${UI_TEST} PRIVATE cxx_std_17)
set_target_properties(${UI_TEST} PROPERTIES AUTOMOC ON AUTOUI ON)
