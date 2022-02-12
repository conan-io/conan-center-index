cmake_minimum_required(VERSION 3.1.2)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

if (MSVC)
	set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} /Z7")
	set(CMAKE_C_FLAGS_DEBUG "${CMAKE_C_FLAGS_DEBUG} /Z7")
endif ()

add_subdirectory("source_subfolder")
