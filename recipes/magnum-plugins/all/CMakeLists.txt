cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

# The original project uses the path to the 'magnum' package, in Conan we cannot modify existing package
set(MAGNUM_INCLUDE_INSTALL_DIR ${CMAKE_INSTALL_PREFIX}/include/Magnum)
set(MAGNUM_EXTERNAL_INCLUDE_INSTALL_DIR ${CMAKE_INSTALL_PREFIX}/include/MagnumExternal)
set(MAGNUM_PLUGINS_INCLUDE_INSTALL_DIR ${CMAKE_INSTALL_PREFIX}/include/MagnumPlugins)


add_subdirectory("source_subfolder")
