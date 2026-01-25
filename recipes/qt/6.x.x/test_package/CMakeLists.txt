cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(Qt6 COMPONENTS Core Network Concurrent REQUIRED CONFIG)
find_package(Qt6 COMPONENTS Xml Sql QUIET CONFIG)

if (IOS)
    qt_add_executable(${PROJECT_NAME} MACOSX_BUNDLE test_package.cpp greeter.h example.qrc)
    qt_import_plugins(${PROJECT_NAME} INCLUDE Qt6::QIOSIntegrationPlugin)
    set_target_properties(${PROJECT_NAME} PROPERTIES
        QT_IOS_LAUNCH_SCREEN "${CMAKE_CURRENT_SOURCE_DIR}/LaunchScreen.storyboard"
    )
else()
    add_executable(${PROJECT_NAME} test_package.cpp greeter.h example.qrc)
endif()
target_link_libraries(${PROJECT_NAME} PRIVATE Qt6::Core Qt6::Network Qt6::Concurrent)
if (TARGET Qt6::Xml)
    target_link_libraries(${PROJECT_NAME} PRIVATE Qt6::Xml)
    target_compile_definitions(${PROJECT_NAME} PRIVATE HAVE_QT_XML)
endif()
if (TARGET Qt6::Sql)
    target_link_libraries(${PROJECT_NAME} PRIVATE Qt6::Sql)
    target_compile_definitions(${PROJECT_NAME} PRIVATE HAVE_QT_SQL)
endif()
target_compile_features(${PROJECT_NAME} PRIVATE cxx_std_17)
set_target_properties(${PROJECT_NAME} PROPERTIES AUTOMOC ON AUTORCC ON)

# Only running this Qt macros in macOS
if (APPLE AND NOT IOS)
    # Related to https://github.com/conan-io/conan-center-index/issues/20574
    qt_standard_project_setup()
    qt_add_executable(test_macos_bundle MACOSX_BUNDLE test_macos_bundle.cpp)
    target_link_libraries(test_macos_bundle PRIVATE Qt6::Core)
    target_compile_features(test_macos_bundle PRIVATE cxx_std_17)
endif()
