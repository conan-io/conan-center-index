cmake_minimum_required(VERSION 3.1)
project(cmake_wrapper)

include("${CMAKE_BINARY_DIR}/conanbuildinfo.cmake")
conan_basic_setup()

if (BUILD_SHARED_LIBS AND MSVC)
	# Building a dll	
	add_definitions(-DWEBP_DLL)	
endif()

add_subdirectory("source_subfolder")
