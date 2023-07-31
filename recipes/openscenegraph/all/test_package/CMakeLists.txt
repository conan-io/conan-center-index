cmake_minimum_required(VERSION 3.15)
project(test_package LANGUAGES CXX)

find_package(OpenSceneGraph REQUIRED)

get_property(cache_variables DIRECTORY PROPERTY CACHE_VARIABLES)
foreach(cache_variable ${cache_variables})
	if("${cache_variable}" MATCHES "^OSG_HAS_(WITH_.+)$")
		add_compile_definitions("${CMAKE_MATCH_1}=${${cache_variable}}")
	endif()
endforeach()

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} OPENSCENEGRAPH::OPENSCENEGRAPH)
