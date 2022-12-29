cmake_minimum_required(VERSION 3.1)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

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
target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS} ${PLATFORM_LIBS})
