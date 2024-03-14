cmake_minimum_required(VERSION 3.16)
project(qtffmpegtest LANGUAGES CXX)

# ==============================================
# Configuration

# General Settings
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Qt-Specific Settings
set(OpenGL_GL_PREFERENCE LEGACY)
set(CMAKE_INCLUDE_CURRENT_DIR ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)

# ==============================================
# Dependencies

find_package(ffmpeg COMPONENTS avcodec avformat avutil avdevice avfilter swscale swresample REQUIRED CONFIG)
find_package(libva REQUIRED CONFIG)
find_package(spdlog REQUIRED CONFIG)
find_package(SDL2 REQUIRED CONFIG)
find_package(nlohmann_json REQUIRED CONFIG)

# Find Qt components
find_package( Qt6 COMPONENTS
  Core
  Gui
  OpenGL
  Xml
  Svg
  Network
  Quick
  QuickControls2
  Multimedia
  Qml
  Sql
  Widgets
REQUIRED CONFIG )

# ==============================================
# Sub-directories

set(LIBRARY_NAME "my_lib")

add_subdirectory(src)
