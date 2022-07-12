cmake_minimum_required(VERSION 3.4)
project(semver.c C)

include(conanbuildinfo.cmake)
conan_basic_setup()

set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)

add_library(${CMAKE_PROJECT_NAME} source_subfolder/semver.c)
set_target_properties(${CMAKE_PROJECT_NAME} PROPERTIES 
	PUBLIC_HEADER source_subfolder/semver.h
	C_STANDARD  99) 

install(TARGETS ${CMAKE_PROJECT_NAME}
        RUNTIME DESTINATION bin
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib
	PUBLIC_HEADER DESTINATION include)

