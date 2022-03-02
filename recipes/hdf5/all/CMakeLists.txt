cmake_minimum_required(VERSION 3.1.2)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

if (MSVC)
	add_compile_options("$<$<CONFIG:DEBUG>:/Z7>")
endif ()

add_subdirectory("source_subfolder")

if (MSVC)
	target_link_options(H5detect PRIVATE "$<$<CONFIG:DEBUG>:/DEBUG:NONE>")
	target_link_options(H5make_libsettings PRIVATE "$<$<CONFIG:DEBUG>:/DEBUG:NONE>")
endif ()
