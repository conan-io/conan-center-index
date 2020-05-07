cmake_minimum_required(VERSION 2.8.12)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

# conan created FindXXX.cmake modules that create IMPORTED targets
# that not have the GLOBAL option set. By requiring them here,
# these targets are visible in all the subprojects.
file(GLOB conan_modules "Find*.cmake")
message("modules: ${conan_modules}")
foreach(module ${conan_modules})
    get_filename_component(modname "${module}" NAME)
    string(REGEX MATCH "^Find(.*).cmake$" modmatch "${modname}")
    if(NOT modmatch)
        message(FATAL_ERROR "Not a module?? ${module} (${modname})")
    endif()
    message(STATUS "requiring package ${CMAKE_MATCH_1}")
    find_package("${CMAKE_MATCH_1}" REQUIRED)
endforeach()

add_subdirectory(source_subfolder)
