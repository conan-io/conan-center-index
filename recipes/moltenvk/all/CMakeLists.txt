cmake_minimum_required(VERSION 3.12)
project(MoltenVK)

include(conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

if(NOT (CMAKE_SYSTEM_NAME STREQUAL "Darwin" OR
        CMAKE_SYSTEM_NAME STREQUAL "iOS" OR
        CMAKE_SYSTEM_NAME STREQUAL "tvOS"))
    message(FATAL_ERROR "MoltenVK only supports MacOS, iOS and tvOS")
endif()

option(MVK_WITH_SPIRV_TOOLS "Build MoltenVK without the MVK_EXCLUDE_SPIRV_TOOLS build setting" ON)
option(MVK_BUILD_SHADERCONVERTER_TOOL "Build MoltenVKShaderConverter" ON)

set(MVK_DIR ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder)
set(MVK_INSTALL_TARGETS "")

# PIC required for objects targets linked into shared MoltenVK
if(BUILD_SHARED_LIBS)
    set(CMAKE_POSITION_INDEPENDENT_CODE ON)
endif()

# Find mandatory Apple Frameworks
function(find_library_required foundVar framework)
    find_library(${foundVar} ${framework})
    if(NOT ${foundVar})
        message(FATAL_ERROR "${framework} framework not found")
    endif()
endfunction()

find_library_required(METAL_FRAMEWORK Metal)
find_library_required(FOUNDATION_FRAMEWORK Foundation)
find_library_required(QUARTZ_CORE_FRAMEWORK QuartzCore)
find_library_required(APPKIT_FRAMEWORK AppKit)
find_library_required(IOSURFACE_FRAMEWORK IOSurface)
if(CMAKE_SYSTEM_NAME STREQUAL "Darwin")
    find_library_required(IO_OR_UI_KIT_FRAMEWORK IOKit)
else()
    find_library_required(IO_OR_UI_KIT_FRAMEWORK UIKit)
endif()

# MoltenVKCommon
# * direct dependencies:
#   - external: None
#   - internal: None
#   - frameworks: Foundation
file(GLOB MVK_COMMON_SOURCES ${MVK_DIR}/common/*.mm)
add_library(MoltenVKCommon OBJECT ${MVK_COMMON_SOURCES})
target_include_directories(MoltenVKCommon PUBLIC ${MVK_DIR}/common)
target_compile_definitions(MoltenVKCommon PRIVATE $<$<CONFIG:Debug>:DEBUG=1>)
target_link_libraries(MoltenVKCommon PRIVATE ${FOUNDATION_FRAMEWORK})

# MoltenVKShaderConverter
# * direct dependencies:
#   - external: spirv-cross, glslang, and spirv-tools (optional)
#   - internal: MoltenVKCommon
#   - frameworks: Foundation
if(MVK_VERSION VERSION_LESS "1.1.0")
    file(GLOB MVK_SC_CONVERTERS_SOURCES
        ${MVK_DIR}/MoltenVKShaderConverter/MoltenVKGLSLToSPIRVConverter/*.cpp
        ${MVK_DIR}/MoltenVKShaderConverter/MoltenVKGLSLToSPIRVConverter/*.mm
        ${MVK_DIR}/MoltenVKShaderConverter/MoltenVKSPIRVToMSLConverter/*.cpp
        ${MVK_DIR}/MoltenVKShaderConverter/MoltenVKSPIRVToMSLConverter/*.mm
    )
else()
    file(GLOB MVK_SC_CONVERTERS_SOURCES
        ${MVK_DIR}/MoltenVKShaderConverter/MoltenVKShaderConverter/*.cpp
        ${MVK_DIR}/MoltenVKShaderConverter/MoltenVKShaderConverter/*.mm
    )
endif()
if(MVK_VERSION VERSION_LESS "1.1.4")
    file(GLOB MVK_SC_COMMON_SOURCES ${MVK_DIR}/MoltenVKShaderConverter/common/*.cpp)
    list(APPEND MVK_SC_CONVERTERS_SOURCES ${MVK_SC_COMMON_SOURCES})
endif()
add_library(MoltenVKShaderConverter OBJECT ${MVK_SC_CONVERTERS_SOURCES})
target_compile_features(MoltenVKShaderConverter PUBLIC cxx_std_11)
target_include_directories(MoltenVKShaderConverter
    PRIVATE ${MVK_DIR}/MoltenVKShaderConverter/common
    INTERFACE ${MVK_DIR}/MoltenVKShaderConverter
)
if(MVK_VERSION VERSION_LESS "1.1.0")
    target_include_directories(MoltenVKShaderConverter PRIVATE
        ${MVK_DIR}/MoltenVKShaderConverter/MoltenVKSPIRVToMSLConverter
    )
endif()
target_link_libraries(MoltenVKShaderConverter
    PRIVATE
        CONAN_PKG::glslang
        MoltenVKCommon
        ${FOUNDATION_FRAMEWORK}
    PUBLIC
        CONAN_PKG::spirv-cross
)
if(MVK_WITH_SPIRV_TOOLS)
    target_link_libraries(MoltenVKShaderConverter PRIVATE CONAN_PKG::spirv-tools)
else()
    target_compile_definitions(MoltenVKShaderConverter PRIVATE MVK_EXCLUDE_SPIRV_TOOLS)
endif()

# MoltenVKShaderConverterTool
# * direct dependencies:
#   - external: None
#   - internal: MoltenVKShaderConverter and MoltenVKCommon
#   - frameworks: Metal and Foundation
if(MVK_BUILD_SHADERCONVERTER_TOOL)
    file(GLOB MVK_SCT_SOURCES
        ${MVK_DIR}/MoltenVKShaderConverter/MoltenVKShaderConverterTool/*.cpp
        ${MVK_DIR}/MoltenVKShaderConverter/MoltenVKShaderConverterTool/*.mm
    )
    add_executable(MoltenVKShaderConverterTool ${MVK_SCT_SOURCES})
    target_compile_features(MoltenVKShaderConverterTool PRIVATE cxx_std_11)
    set_property(TARGET MoltenVKShaderConverterTool PROPERTY OUTPUT_NAME "MoltenVKShaderConverter")
    target_include_directories(MoltenVKShaderConverterTool PRIVATE
        ${MVK_DIR}/MoltenVKShaderConverter/common
    )
    if(MVK_VERSION VERSION_LESS "1.1.0")
        target_include_directories(MoltenVKShaderConverterTool PRIVATE
            ${MVK_DIR}/MoltenVKShaderConverter/MoltenVKGLSLToSPIRVConverter
            ${MVK_DIR}/MoltenVKShaderConverter/MoltenVKSPIRVToMSLConverter
        )
    else()
        target_include_directories(MoltenVKShaderConverterTool PRIVATE
            ${MVK_DIR}/MoltenVKShaderConverter/MoltenVKShaderConverter
        )
    endif()
    target_link_libraries(MoltenVKShaderConverterTool PRIVATE
        MoltenVKCommon
        MoltenVKShaderConverter
        ${METAL_FRAMEWORK}
        ${FOUNDATION_FRAMEWORK}
    )
    list(APPEND MVK_INSTALL_TARGETS MoltenVKShaderConverterTool)
endif()

# MoltenVK
# * direct dependencies:
#   - external: cereal, spirv-cross and vulkan-headers (+ vulkan-portability if moltenvk < 1.1.0)
#   - internal: MoltenVKShaderConverter and MoltenVKCommon
#   - frameworks: Foundation, Metal, QuartzCore, AppKit, IOSurface + IOKit (Macos) or UIKit (iOS/tvOS)
file(GLOB_RECURSE MVK_SOURCES
    ${MVK_DIR}/MoltenVK/*.m
    ${MVK_DIR}/MoltenVK/*.mm
    ${MVK_DIR}/MoltenVK/*.cpp
)
add_library(MoltenVK ${MVK_SOURCES})
target_compile_features(MoltenVK PUBLIC cxx_std_11)
target_include_directories(MoltenVK PRIVATE
    ${MVK_DIR}/MoltenVK/MoltenVK/API
    ${MVK_DIR}/MoltenVK/MoltenVK/Commands
    ${MVK_DIR}/MoltenVK/MoltenVK/GPUObjects
    ${MVK_DIR}/MoltenVK/MoltenVK/Layers
    ${MVK_DIR}/MoltenVK/MoltenVK/OS
    ${MVK_DIR}/MoltenVK/MoltenVK/Utility
    ${MVK_DIR}/MoltenVK/MoltenVK/Vulkan
)
target_link_libraries(MoltenVK
    PRIVATE
        CONAN_PKG::cereal
        CONAN_PKG::spirv-cross
        MoltenVKCommon
        MoltenVKShaderConverter
        ${FOUNDATION_FRAMEWORK}
        ${QUARTZ_CORE_FRAMEWORK}
        ${APPKIT_FRAMEWORK}
        ${IO_OR_UI_KIT_FRAMEWORK}
    PUBLIC
        CONAN_PKG::vulkan-headers
        ${METAL_FRAMEWORK}
        ${IOSURFACE_FRAMEWORK}
)
if(MVK_VERSION VERSION_LESS "1.1.0")
    target_link_libraries(MoltenVK PUBLIC CONAN_PKG::vulkan-portability)
endif()
target_compile_options(MoltenVK PRIVATE
    -Wno-unguarded-availability-new
    -Wno-deprecated-declarations
    -Wno-nonportable-include-path
    -Wno-tautological-pointer-compare
)
list(APPEND MVK_INSTALL_TARGETS MoltenVK)

# Custom Target to generate internal header file required by MoltenVK target.
# This header should contain:
#  - if moltenvk < 1.44 : spirv-cross commit hash in spirvCrossRevisionString variable
#  - if moltenvk >= 1.44: moltenvk commit hash in mvkRevString variable (but we still
#    use spirv-cross commit hash, since MoltenVK hash is not available in this context,
#    and hash value is no really important)
set(MVK_REV_FILE ${MVK_DIR}/ExternalRevisions/SPIRV-Cross_repo_revision)
set(MVK_REV_HEADER_DIR ${CMAKE_CURRENT_BINARY_DIR}/mvk_hash_generated)
if(MVK_VERSION VERSION_LESS "1.0.44")
    set(MVK_REV_HEADER ${MVK_REV_HEADER_DIR}/SPIRV-Cross/mvkSpirvCrossRevisionDerived.h)
    set(MVK_REV_VAR_NAME "spirvCrossRevisionString")
else()
    set(MVK_REV_HEADER ${MVK_REV_HEADER_DIR}/mvkGitRevDerived.h)
    set(MVK_REV_VAR_NAME "mvkRevString")
endif()
set(MVK_REV_DEFINES -DMVK_REV_FILE=${MVK_REV_FILE} -DMVK_REV_HEADER=${MVK_REV_HEADER} -DMVK_REV_VAR_NAME=${MVK_REV_VAR_NAME})
set(MVK_REV_GEN_SCRIPT "${CMAKE_CURRENT_BINARY_DIR}/mvk_git_hash_generator.cmake")
file(WRITE ${MVK_REV_GEN_SCRIPT}
    "file(READ \${MVK_REV_FILE} MVK_SPIRV_CROSS_GIT_REV)\n"
    "string(REPLACE \"\\n\" \"\" MVK_SPIRV_CROSS_GIT_REV \${MVK_SPIRV_CROSS_GIT_REV})\n"
    "file(WRITE \${MVK_REV_HEADER} \"static const char* \${MVK_REV_VAR_NAME} = \\\"\${MVK_SPIRV_CROSS_GIT_REV}\\\";\")\n"
)
add_custom_target(mvk-commit-hash-header DEPENDS ${MVK_REV_HEADER})
add_custom_command(
    COMMENT "Create ${MVK_REV_HEADER}"
    OUTPUT ${MVK_REV_HEADER}
    DEPENDS ${MVK_REV_FILE}
    COMMAND ${CMAKE_COMMAND} ${MVK_REV_DEFINES} -P ${MVK_REV_GEN_SCRIPT}
)
add_dependencies(MoltenVK mvk-commit-hash-header)
target_include_directories(MoltenVK PRIVATE ${MVK_REV_HEADER_DIR})

# Installation
install(
    TARGETS ${MVK_INSTALL_TARGETS}
    BUNDLE DESTINATION ${CMAKE_INSTALL_BINDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
)

if(BUILD_SHARED_LIBS)
    install(
        FILES ${MVK_DIR}/MoltenVK/icd/MoltenVK_icd.json
        DESTINATION ${CMAKE_INSTALL_LIBDIR}
    )
endif()

file(GLOB MVK_PUBLIC_HEADERS ${MVK_DIR}/MoltenVK/MoltenVK/API/*.h)
install(
    FILES ${MVK_PUBLIC_HEADERS}
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/MoltenVK
)

if(MVK_VERSION VERSION_LESS "1.1.0")
    file(GLOB MVK_SC_PUBLIC_HEADERS
        ${MVK_DIR}/MoltenVKShaderConverter/MoltenVKGLSLToSPIRVConverter/*Conversion.h
        ${MVK_DIR}/MoltenVKShaderConverter/MoltenVKGLSLToSPIRVConverter/*Converter.h
        ${MVK_DIR}/MoltenVKShaderConverter/MoltenVKSPIRVToMSLConverter/*Conversion.h
        ${MVK_DIR}/MoltenVKShaderConverter/MoltenVKSPIRVToMSLConverter/*Converter.h
    )
else()
    file(GLOB MVK_SC_PUBLIC_HEADERS
        ${MVK_DIR}/MoltenVKShaderConverter/MoltenVKShaderConverter/*Conversion.h
        ${MVK_DIR}/MoltenVKShaderConverter/MoltenVKShaderConverter/*Converter.h
    )
endif()
install(
    FILES ${MVK_SC_PUBLIC_HEADERS}
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}/MoltenVKShaderConverter
)
