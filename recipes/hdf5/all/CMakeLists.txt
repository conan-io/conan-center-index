cmake_minimum_required(VERSION 3.1.2)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

if (MSVC)
	add_compile_options($<$<C_COMPILER_ID:MSVC>:/Z7)
endif ()

add_subdirectory("source_subfolder")
