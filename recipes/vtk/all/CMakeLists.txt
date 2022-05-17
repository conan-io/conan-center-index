# Ensure this cmake minimum matches what is in conanfile.py
cmake_minimum_required(VERSION 3.22.4 FATAL_ERROR)
project(cmake_wrapper)

set (CMAKE_FIND_DEBUG_MODE TRUE)

if (NOT CMAKE_FIND_PACKAGE_PREFER_CONFIG)
   message (FATAL_ERROR "PAUL prefer-config should be ON, as this will prioritise conan finders over VTK's module finders, which come first in the list")
endif ()

# Make SURE this is disabled, otherwise chaos reins
# if (CMAKE_FIND_PACKAGE_PREFER_CONFIG)
# message (FATAL_ERROR "You must add to profile: [conf] tools.cmake.cmaketoolchain:find_package_prefer_config=False, otherwise bug: https://github.com/conan-io/conan/issues/10387")
# endif ()


# include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
# conan_basic_setup(KEEP_RPATHS)
#
# 
# if (APPLE)
# 	set(CMAKE_INSTALL_RPATH "@executable_path/../lib")
# else()
# 	set(CMAKE_INSTALL_RPATH "$ORIGIN/../lib")
# endif()
# 
# set(CMAKE_BUILD_WITH_INSTALL_RPATH ON)
# 
# if(MSVC)
#     # Remove pdb-related flags
#     string(REGEX REPLACE "/Z[iI7]" ""
#         CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG}")
#     # Embed debug info into .lib-files
#     set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_RELEASE} /Z7")
# endif()

add_subdirectory(source_subfolder)
