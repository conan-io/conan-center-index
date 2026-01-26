cmake_minimum_required(VERSION 3.8)
project(test_package LANGUAGES CXX)

find_package(Qt6 COMPONENTS Core Gui Network Concurrent REQUIRED CONFIG)
find_package(Qt6 COMPONENTS Xml Sql QUIET CONFIG)

if (IOS)
    qt_add_executable(${PROJECT_NAME} MACOSX_BUNDLE test_package.cpp greeter.h example.qrc)
    qt_import_plugins(${PROJECT_NAME} INCLUDE Qt6::QIOSIntegrationPlugin)
    set_target_properties(${PROJECT_NAME} PROPERTIES
        QT_IOS_LAUNCH_SCREEN "${CMAKE_CURRENT_SOURCE_DIR}/LaunchScreen.storyboard"
        MACOSX_BUNDLE_INFO_PLIST "${CMAKE_CURRENT_SOURCE_DIR}/Info.plist.app.in"
    )
    # On iOS, plugins are static libraries and must be linked directly
    # Extract Qt package root from CMAKE_PREFIX_PATH
    # CMAKE_PREFIX_PATH contains paths like /path/to/qt/lib/cmake/Qt6Core
    set(QIOS_PLUGIN_LIB "")
    foreach(PREFIX_PATH ${CMAKE_PREFIX_PATH})
        # Check if this path contains /lib/cmake/Qt6 (indicates Qt package)
        string(FIND "${PREFIX_PATH}" "/lib/cmake/Qt6" QT6_INDEX)
        if (NOT QT6_INDEX EQUAL -1)
            # Extract the part before /lib/cmake/Qt6
            string(SUBSTRING "${PREFIX_PATH}" 0 ${QT6_INDEX} QT6_PACKAGE_ROOT)
            set(QIOS_PLUGIN_PATH "${QT6_PACKAGE_ROOT}/plugins/platforms/libqios.a")
            if (EXISTS "${QIOS_PLUGIN_PATH}")
                set(QIOS_PLUGIN_LIB "${QIOS_PLUGIN_PATH}")
                message(STATUS "Found iOS plugin at: ${QIOS_PLUGIN_PATH}")
                break()
            endif()
        endif()
    endforeach()

    # Fallback: Use QT_PACKAGE_FOLDER if provided
    if (NOT QIOS_PLUGIN_LIB AND DEFINED QT_PACKAGE_FOLDER)
        set(QIOS_PLUGIN_PATH "${QT_PACKAGE_FOLDER}/plugins/platforms/libqios.a")
        if (EXISTS "${QIOS_PLUGIN_PATH}")
            set(QIOS_PLUGIN_LIB "${QIOS_PLUGIN_PATH}")
            message(STATUS "Found iOS plugin via QT_PACKAGE_FOLDER: ${QIOS_PLUGIN_PATH}")
        endif()
    endif()

    if (QIOS_PLUGIN_LIB)
        # Link the static library
        target_link_libraries(${PROJECT_NAME} PRIVATE "${QIOS_PLUGIN_LIB}")
        # Get frameworks from Qt6::QIOSIntegrationPlugin target if available
        set(IOS_FRAMEWORKS_LIST "")
        if (TARGET Qt6::QIOSIntegrationPlugin)
            get_target_property(QIOS_FRAMEWORKS Qt6::QIOSIntegrationPlugin INTERFACE_LINK_FRAMEWORKS)
            if (QIOS_FRAMEWORKS)
                set(IOS_FRAMEWORKS_LIST ${QIOS_FRAMEWORKS})
            endif()
        endif()
        # Fallback to hardcoded list if target doesn't provide frameworks
        if (NOT IOS_FRAMEWORKS_LIST)
            set(IOS_FRAMEWORKS_LIST
                AudioToolbox Foundation Metal QuartzCore UIKit CoreGraphics
                AssetsLibrary UniformTypeIdentifiers Photos CoreFoundation
            )
        endif()
        # Link all required frameworks
        foreach(FRAMEWORK ${IOS_FRAMEWORKS_LIST})
            find_library(${FRAMEWORK}_LIB ${FRAMEWORK})
            if (${FRAMEWORK}_LIB)
                target_link_libraries(${PROJECT_NAME} PRIVATE ${${FRAMEWORK}_LIB})
            endif()
        endforeach()
        # Ensure Objective-C runtime is linked (required for iOS)
        find_library(OBJC_LIB objc)
        if (OBJC_LIB)
            target_link_libraries(${PROJECT_NAME} PRIVATE ${OBJC_LIB})
        endif()
        message(STATUS "Linked iOS plugin: ${QIOS_PLUGIN_LIB}")
    else()
        message(FATAL_ERROR "Could not find iOS plugin libqios.a. CMAKE_PREFIX_PATH=${CMAKE_PREFIX_PATH}")
    endif()
else()
    add_executable(${PROJECT_NAME} test_package.cpp greeter.h example.qrc)
endif()
target_link_libraries(${PROJECT_NAME} PRIVATE Qt6::Core Qt6::Gui Qt6::Network Qt6::Concurrent)
if (IOS AND TARGET Qt6::EntryPointPrivate)
    target_link_libraries(${PROJECT_NAME} PRIVATE Qt6::EntryPointPrivate)
endif()
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
