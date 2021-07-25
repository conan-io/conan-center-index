cmake_minimum_required(VERSION 3.4)

project(geotrans VERSION 3.8 LANGUAGES CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

file(GLOB_RECURSE LIB_SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/CCS/src/*.cpp")

add_library(geotrans ${LIB_SOURCES})

target_compile_features(geotrans PUBLIC cxx_std_11)
target_compile_options(geotrans PRIVATE -pthread -Wno-deprecated)

file(GLOB_RECURSE LIB_HEADERS "${CMAKE_CURRENT_SOURCE_DIR}/CCS/src/*.h")
set(INCLUDE_DIRS "")

foreach(file ${LIB_HEADERS})
    get_filename_component(DIR_PATH ${file} PATH)
    set(INCLUDE_DIRS ${INCLUDE_DIRS} ${DIR_PATH})
endforeach()
list(REMOVE_DUPLICATES INCLUDE_DIRS)

target_include_directories(geotrans PUBLIC include ${INCLUDE_DIRS})
