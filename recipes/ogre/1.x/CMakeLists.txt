cmake_minimum_required(VERSION 3.15)
project(OGRE)

macro(custom_find_package name)
    find_package(${name} ${ARGN}
        # Allow only Conan packages
        NO_DEFAULT_PATH
        PATHS ${CMAKE_PREFIX_PATH}
    )
    string(TOUPPER ${name} name_upper)
    set(${name_upper}_FOUND TRUE)
    set(${name_upper}_VERSION_STRING ${${name}_VERSION_STRING})
    set(${name_upper}_INCLUDE_DIRS ${${name}_INCLUDE_DIRS})
    set(${name_upper}_INCLUDE_DIR ${${name}_INCLUDE_DIR})
    set(${name_upper}_LIBRARIES ${${name}_LIBRARIES})
    set(${name_upper}_DEFINITIONS ${${name}_DEFINITIONS})
    unset(name_upper)
endmacro()

# Do not allow system Qt to be used by accident
set(CMAKE_DISABLE_FIND_PACKAGE_QT TRUE)
set(CMAKE_DISABLE_FIND_PACKAGE_Qt5 TRUE)
set(CMAKE_DISABLE_FIND_PACKAGE_Qt6 TRUE)

custom_find_package(FreeImage QUIET CONFIG)
custom_find_package(Freetype QUIET CONFIG)
custom_find_package(OpenEXR QUIET CONFIG)
custom_find_package(assimp QUIET CONFIG)
custom_find_package(pugixml REQUIRED CONFIG)

add_subdirectory(src)

if(TARGET Codec_FreeImage)
    target_link_libraries(Codec_FreeImage PUBLIC freeimage::freeimage)
endif()
if(TARGET Codec_EXR)
    target_link_libraries(Codec_EXR openexr::openexr)
endif()
if(TARGET OgreOverlay)
    target_link_libraries(OgreOverlay PUBLIC Freetype::Freetype)
endif()
if(TARGET Plugin_DotScene)
    target_link_libraries(Plugin_DotScene PUBLIC pugixml::pugixml)
endif()
if(TARGET OgreXMLConverter)
    target_link_libraries(OgreXMLConverter pugixml::pugixml)
endif()
