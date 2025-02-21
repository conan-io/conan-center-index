cmake_minimum_required(VERSION 3.15)
project(PackageTest CXX)
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(openfx CONFIG REQUIRED)

add_library(test_package SHARED src/invert.cpp)
target_include_directories(test_package PUBLIC ${openfx_INCLUDE_DIRS})
target_link_libraries(test_package openfx::Api)

if(WIN32)
    set_target_properties(test_package PROPERTIES SUFFIX ".ofx")
else()
    set_target_properties(test_package PROPERTIES PREFIX "" SUFFIX ".ofx")
endif()

# file(GLOB_RECURSE PLUGIN_SOURCES "../Support/Plugins/Invert/*.cpp")
# add_ofx_plugin(invert_plugin ../Support/Plugins/Invert)
# target_sources(invert_plugin PUBLIC ${PLUGIN_SOURCES})
# target_include_directories(invert_plugin PUBLIC ${openfx_INCLUDE_DIRS})
# target_link_libraries(invert_plugin openfx::Support)
