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

set(DILIGENT_ARGS_DIR ${CONAN_INCLUDE_DIRS_TAYWEE-ARGS})
set(DILIGENT_DEAR_IMGUI_PATH ${CONAN_INCLUDE_DIRS_IMGUI})

add_subdirectory(source_subfolder)
