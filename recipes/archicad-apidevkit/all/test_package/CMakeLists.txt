cmake_minimum_required(VERSION 3.1)

function(SetCompilerOptions target ac_version)
    if(${ac_version} EQUAL "27")
        target_compile_features(${target} PUBLIC cxx_std_17)
    else()
        target_compile_features(${target} PUBLIC cxx_std_14)
    endif()

    target_compile_options(${target} PUBLIC "$<$<CONFIG:Debug>:-DDEBUG>")

    if(WIN32)
        target_compile_options(${target} PUBLIC /W4 /WX
            /Zc:wchar_t-
            /wd4499
            /EHsc
        )
    else()
        target_compile_options(${target} PUBLIC -Wall -Wextra -Werror
            -fvisibility=hidden
            -Wno-multichar
            -Wno-ctor-dtor-privacy
            -Wno-invalid-offsetof
            -Wno-ignored-qualifiers
            -Wno-reorder
            -Wno-overloaded-virtual
            -Wno-unused-parameter
            -Wno-deprecated)
    endif()
endfunction()

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
set(CONAN_DISABLE_CHECK_COMPILER true)
conan_basic_setup(TARGETS)
set(API_DEVKIT_DIR ${CONAN_ARCHICAD-APIDEVKIT_ROOT})
set(AC_API_DEVKIT_DIR ${API_DEVKIT_DIR} CACHE PATH "API DevKit directory.")

# Test components
find_package(archicad-apidevkit COMPONENTS GSRoot CONFIG)

set(ACAPINC_FILE_LOCATION ${AC_API_DEVKIT_DIR}/Inc/ACAPinc.h)

if(EXISTS ${ACAPINC_FILE_LOCATION})
    file(READ ${ACAPINC_FILE_LOCATION} ACAPIncContent)
    string(REGEX MATCHALL "#define[ \t]+ServerMainVers_([0-9][0-9])" VersionList ${ACAPIncContent})
    set(ARCHICAD_VERSION ${CMAKE_MATCH_1})
    message(STATUS "Archicad Version: ${ARCHICAD_VERSION}")
else()
    message(FATAL_ERROR "Failed to detect Archicad version, please check the value of the AC_API_DEVKIT_DIR variable.")
endif()

if(WIN32)
    add_definitions(-DUNICODE -D_UNICODE)
else()
    add_definitions(-Dmacintosh=1)
endif()

add_definitions(-DACExtension)

project("test_package")

add_executable(test_package test_gsroot.cpp)
SetCompilerOptions(test_package ARCHICAD_VERSION)
target_include_directories(test_package PUBLIC ${AC_API_DEVKIT_DIR}/Modules/GSRoot)
set_property(TARGET test_package PROPERTY CXX_STANDARD 11)
