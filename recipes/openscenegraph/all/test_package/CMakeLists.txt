cmake_minimum_required(VERSION 3.1.2)
project(test_package)

include(${PROJECT_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

find_package(OpenSceneGraph REQUIRED)

include_directories(${OPENSCENEGRAPH_INCLUDE_DIRS})
link_libraries(${OPENSCENEGRAPH_LIBRARIES})
add_compile_definitions(${OPENSCENEGRAPH_COMPILE_DEFINITIONS})


get_property(cache_variables DIRECTORY PROPERTY CACHE_VARIABLES)
foreach(cache_variable ${cache_variables})
	if("${cache_variable}" MATCHES "^OSG_HAS_(WITH_.+)$")
		add_compile_definitions("${CMAKE_MATCH_1}=${${cache_variable}}")
	endif()
endforeach()

add_executable(${PROJECT_NAME} test_package.cpp)
