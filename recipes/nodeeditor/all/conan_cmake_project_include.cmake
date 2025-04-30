# INFO: The project Nodeeditor uses CMake Qt macros qt_add_resources and qt_wrap_cpp
# in order to manage resources and not CMake AUTOMOC target property.
# These macros do not use CMAKE_AUTOMOC_EXECUTABLE, but are imported executables.
# We need to reconfigure their paths to the ones from Conan package in order to avoid
# runtime errors related to missing dynamic libraries in DYLD_LIBRARY_PATH.

cmake_minimum_required(VERSION 3.15)

find_package(QT NAMES Qt6 REQUIRED)

if(TARGET ${QT_CMAKE_EXPORT_NAMESPACE}::moc)
    set_target_properties(${QT_CMAKE_EXPORT_NAMESPACE}::moc PROPERTIES
        IMPORTED_LOCATION "${CMAKE_AUTOMOC_EXECUTABLE}"
    )
endif()

if(TARGET ${QT_CMAKE_EXPORT_NAMESPACE}::rcc)
    set_target_properties(${QT_CMAKE_EXPORT_NAMESPACE}::rcc PROPERTIES
        IMPORTED_LOCATION "${CMAKE_AUTORCC_EXECUTABLE}"
    )
endif()
