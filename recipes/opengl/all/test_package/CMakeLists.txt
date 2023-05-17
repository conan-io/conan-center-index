cmake_minimum_required(VERSION 3.10)
project(test_package)

find_package(opengl_system REQUIRED CONFIG)

set(SOURCES test_package.cpp)

if(WIN32)
    list(APPEND SOURCES win.cpp)
endif()

if(APPLE)
    list(APPEND SOURCES osx.mm)
    set_source_files_properties(osx.mm PROPERTIES COMPILE_FLAGS "-x objective-c++")

    list(APPEND PLATFORM_LIBS "objc")

    find_library(APPKIT_LIBRARY AppKit)
    find_library(FOUNDATION_LIBRARY Foundation)

    if(APPKIT_LIBRARY)
        list(APPEND PLATFORM_LIBS ${APPKIT_LIBRARY})
    endif()

    if(FOUNDATION_LIBRARY)
        list(APPEND PLATFORM_LIBS ${FOUNDATION_LIBRARY})
    endif()
endif()

add_executable(${PROJECT_NAME} ${SOURCES})
target_link_libraries(${PROJECT_NAME} PRIVATE opengl::opengl ${PLATFORM_LIBS})
