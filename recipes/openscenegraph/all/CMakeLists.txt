cmake_minimum_required(VERSION 3.1.2)
project(cmake_wrapper)

include(${PROJECT_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(NO_OUTPUT_DIRS)

# Hack to insure that conan's copy of these are used, rather than CMake's
# If this isn't here, find_package(X11) will pull in CMake's copy
find_package(Freetype QUIET)
find_package(Fontconfig QUIET)

# Workaround limitations of the cmake_find_package generator
set(FREETYPE_FOUND ${Freetype_FOUND})
if(FREETYPE_FOUND)
    set(FREETYPE_LIBRARIES ${Freetype_LIBRARIES})
    set(FREETYPE_INCLUDE_DIRS ${Freetype_INCLUDE_DIRS})
endif()

if(APPLE)
    add_compile_definitions("GL_SILENCE_DEPRECATION")
endif()

add_subdirectory("source_subfolder")
