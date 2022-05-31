cmake_minimum_required(VERSION 3.13)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup(TARGETS KEEP_RPATHS)

if (MSVC)
	add_compile_options("$<$<CONFIG:DEBUG>:/Z7>")
	add_link_options("$<$<CONFIG:DEBUG>:/DEBUG:NONE>")
endif ()

add_subdirectory("source_subfolder")
