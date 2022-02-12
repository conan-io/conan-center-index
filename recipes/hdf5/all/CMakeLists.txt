cmake_minimum_required(VERSION 3.1.2)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

if (MSVC)
	set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /Z7")
	set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} /Z7")
endif ()

add_subdirectory("source_subfolder")
