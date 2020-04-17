cmake_minimum_required(VERSION 2.8.12)
project(test_package CXX)

set(CMAKE_MODULE_PATH ${CMAKE_BINARY_DIR})

# Force test_package to be generated in build_folder (CMAKE_BINARY_DIR) 
# so we get same behaviour between Unix Makefiles & Visual studio generator 

# First for the generic no-config case (e.g. with mingw)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})
# Second, for multi-config builds (e.g. msvc)
foreach(OUTPUTCONFIG ${CMAKE_CONFIGURATION_TYPES})
    string(TOUPPER ${OUTPUTCONFIG} OUTPUTCONFIG)
    set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_${OUTPUTCONFIG} ${CMAKE_BINARY_DIR})
endforeach(OUTPUTCONFIG CMAKE_CONFIGURATION_TYPES)

find_package(Backward REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE Backward::Backward)
