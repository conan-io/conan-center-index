cmake_minimum_required(VERSION 3.2)
project(cmake_wrapper)

include(BuildUtils.cmake)

include(conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

find_package(imgui REQUIRED)
find_package(PNG REQUIRED)
find_package(TIFF REQUIRED)
find_package(JPEG REQUIRED)
find_package(ZLIB REQUIRED)
find_package(args CONFIG)
find_package(diligent-core REQUIRED)

set(Diligent-GraphicsEngine_SOURCE_DIR ${CONAN_DILIGENT-CORE_ROOT}/include/DiligentCore/Graphics/GraphicsEngine/)
set(DILIGENT_ARGS_DIR ${CONAN_INCLUDE_DIRS_TAYWEE-ARGS})
set(DILIGENT_DEAR_IMGUI_PATH ${CONAN_INCLUDE_DIRS_IMGUI})

add_library(Diligent-BuildSettings           ALIAS diligent-core::diligent-core)
add_library(Diligent-Common                  ALIAS diligent-core::diligent-core)
add_library(Diligent-PlatformInterface       ALIAS diligent-core::diligent-core)
add_library(Diligent-GraphicsEngineInterface ALIAS diligent-core::diligent-core)
add_library(Diligent-GraphicsAccessories     ALIAS diligent-core::diligent-core)
add_library(Diligent-GraphicsTools           ALIAS diligent-core::diligent-core)
add_library(Diligent-Archiver-static         ALIAS diligent-core::diligent-core)
add_library(imgui ALIAS imgui::imgui)

add_subdirectory(source_subfolder)
set_target_properties(Diligent-RenderStateNotation PROPERTIES EXCLUDE_FROM_ALL 1 EXCLUDE_FROM_DEFAULT_BUILD 1)

