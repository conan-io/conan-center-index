cmake_minimum_required(VERSION 3.1)
project(MoltenVK)

include(conanbuildinfo.cmake)
conan_basic_setup()

if(NOT (CMAKE_SYSTEM_NAME STREQUAL "Darwin" OR
        CMAKE_SYSTEM_NAME STREQUAL "iOS" OR
        CMAKE_SYSTEM_NAME STREQUAL "tvOS"))
    message(FATAL_ERROR "MoltenVK only supports MacOS, iOS and tvOS")
endif()

option(MVK_WITH_SPIRV_TOOLS "Build MoltenVK without the MVK_EXCLUDE_SPIRV_TOOLS build setting" ON)
option(MVK_BUILD_SHADERCONVERTER_TOOL "Build MoltenVKShaderConverter" ON)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS ON)

add_compile_options(
    -Wno-unguarded-availability-new
    -Wno-deprecated-declarations
    -Wno-nonportable-include-path
)

# PIC required for objects targets linked into shared MoltenVK
if(BUILD_SHARED_LIBS)
    set(CMAKE_POSITION_INDEPENDENT_CODE ON)
endif()

# Required Apple Frameworks
find_library(METAL_FRAMEWORK Metal)
if(NOT METAL_FRAMEWORK)
    message(FATAL_ERROR "Metal framework not found")
endif()
find_library(FOUNDATION_FRAMEWORK Foundation)
if(NOT FOUNDATION_FRAMEWORK)
    message(FATAL_ERROR "Foundation framework not found")
endif()
find_library(QUARTZ_CORE_FRAMEWORK QuartzCore)
if(NOT QUARTZ_CORE_FRAMEWORK)
    message(FATAL_ERROR "QuartzCore framework not found")
endif()
find_library(APPKIT_FRAMEWORK AppKit)
if(NOT APPKIT_FRAMEWORK)
    message(FATAL_ERROR "AppKit framework not found")
endif()
find_library(IOSURFACE_FRAMEWORK IOSurface)
if(NOT IOSURFACE_FRAMEWORK)
    message(FATAL_ERROR "IOSurface framework not found")
endif()
if(CMAKE_SYSTEM_NAME STREQUAL "Darwin")
    find_library(IO_OR_UI_KIT_FRAMEWORK IOKit)
    if(NOT IO_OR_UI_KIT_FRAMEWORK)
        message(FATAL_ERROR "IOKit framework not found")
    endif()
else()
    find_library(IO_OR_UI_KIT_FRAMEWORK UIKit)
    if(NOT IO_OR_UI_KIT_FRAMEWORK)
        message(FATAL_ERROR "UIKit framework not found")
    endif()
endif()

set(PROJECT_DIR ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder)
set(MVK_INSTALL_TARGETS "")

# MoltenVKCommon
# * direct dependencies:
#   - external: None
#   - internal: None
#   - frameworks: Foundation
file(GLOB MVK_COMMON_SOURCES ${PROJECT_DIR}/common/*.mm)
add_library(MoltenVKCommon OBJECT ${MVK_COMMON_SOURCES})
target_compile_definitions(MoltenVKCommon PRIVATE $<$<CONFIG:Debug>:DEBUG=1>)

# MoltenVKShaderConverter
# * direct dependencies:
#   - external: spirv-cross, glslang, and spirv-tools (optional)
#   - internal: MoltenVKCommon
#   - frameworks: Foundation
file(GLOB MVK_SC_SOURCES
    ${PROJECT_DIR}/MoltenVKShaderConverter/common/*.cpp
    ${PROJECT_DIR}/MoltenVKShaderConverter/MoltenVKShaderConverter/*.cpp
    ${PROJECT_DIR}/MoltenVKShaderConverter/MoltenVKShaderConverter/*.mm
)
add_library(MoltenVKShaderConverter OBJECT ${MVK_SC_SOURCES})
target_include_directories(MoltenVKShaderConverter PUBLIC
    ${PROJECT_DIR}/common
    ${PROJECT_DIR}/MoltenVKShaderConverter/common
)
if(NOT MVK_WITH_SPIRV_TOOLS)
    target_compile_definitions(MoltenVKShaderConverter PRIVATE MVK_EXCLUDE_SPIRV_TOOLS)
endif()

# MoltenVKShaderConverterTool
# * direct dependencies:
#   - external: None
#   - internal: MoltenVKShaderConverter and MoltenVKCommon
#   - frameworks: Metal and Foundation
if(MVK_BUILD_SHADERCONVERTER_TOOL)
    file(GLOB MVK_SCT_SOURCES
        ${PROJECT_DIR}/MoltenVKShaderConverter/MoltenVKShaderConverterTool/*.cpp
        ${PROJECT_DIR}/MoltenVKShaderConverter/MoltenVKShaderConverterTool/*.mm
    )
    add_executable(MoltenVKShaderConverterTool ${MVK_SCT_SOURCES})
    set_property(TARGET MoltenVKShaderConverterTool PROPERTY OUTPUT_NAME "MoltenVKShaderConverter")
    target_include_directories(MoltenVKShaderConverterTool PRIVATE
        ${PROJECT_DIR}/MoltenVKShaderConverter/MoltenVKShaderConverter
    )
    target_link_libraries(MoltenVKShaderConverterTool PRIVATE
        MoltenVKCommon
        MoltenVKShaderConverter
        ${CONAN_LIBS}
        ${METAL_FRAMEWORK}
        ${FOUNDATION_FRAMEWORK}
    )
    list(APPEND MVK_INSTALL_TARGETS MoltenVKShaderConverterTool)
endif()

# MoltenVK
# * direct dependencies:
#   - external: cereal, spirv-cross and vulkan-headers
#   - internal: MoltenVKShaderConverter and MoltenVKCommon
#   - frameworks: Foundation, Metal, QuartzCore, AppKit, IOSurface + IOKit (Macos) or UIKit (iOS/tvOS)
file(GLOB_RECURSE MVK_SOURCES
    ${PROJECT_DIR}/MoltenVK/*.m
    ${PROJECT_DIR}/MoltenVK/*.mm
    ${PROJECT_DIR}/MoltenVK/*.cpp
)
add_library(MoltenVK ${MVK_SOURCES})
target_include_directories(MoltenVK PRIVATE
    ${PROJECT_DIR}/Common
    ${PROJECT_DIR}/MoltenVKShaderConverter
    ${PROJECT_DIR}/MoltenVK/MoltenVK/API
    ${PROJECT_DIR}/MoltenVK/MoltenVK/Commands
    ${PROJECT_DIR}/MoltenVK/MoltenVK/GPUObjects
    ${PROJECT_DIR}/MoltenVK/MoltenVK/Layers
    ${PROJECT_DIR}/MoltenVK/MoltenVK/OS
    ${PROJECT_DIR}/MoltenVK/MoltenVK/Utility
    ${PROJECT_DIR}/MoltenVK/MoltenVK/Vulkan
)
target_link_libraries(MoltenVK PRIVATE
    MoltenVKCommon
    MoltenVKShaderConverter
    ${CONAN_LIBS}
    ${METAL_FRAMEWORK}
    ${FOUNDATION_FRAMEWORK}
    ${QUARTZ_CORE_FRAMEWORK}
    ${APPKIT_FRAMEWORK}
    ${IOSURFACE_FRAMEWORK}
    ${IO_OR_UI_KIT_FRAMEWORK}
)
list(APPEND MVK_INSTALL_TARGETS MoltenVK)

install(
    TARGETS ${MVK_INSTALL_TARGETS}
    BUNDLE DESTINATION ${CMAKE_INSTALL_BINDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

if(BUILD_SHARED_LIBS)
    install(
        FILES ${PROJECT_DIR}/MoltenVK/icd/MoltenVK_icd.json
        DESTINATION ${CMAKE_INSTALL_LIBDIR}
    )
endif()

file(GLOB MVK_PUBLIC_HEADERS ${PROJECT_DIR}/MoltenVK/MoltenVK/API/*.h)
install(
    FILES ${MVK_PUBLIC_HEADERS}
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/MoltenVK
)

file(GLOB MVK_SC_PUBLIC_HEADERS
    ${PROJECT_DIR}/MoltenVKShaderConverter/MoltenVKShaderConverter/*Conversion.h
    ${PROJECT_DIR}/MoltenVKShaderConverter/MoltenVKShaderConverter/*Converter.h
)
install(
    FILES ${MVK_SC_PUBLIC_HEADERS}
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/MoltenVKShaderConverter
)
