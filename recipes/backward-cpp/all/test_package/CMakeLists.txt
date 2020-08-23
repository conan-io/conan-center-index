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

if (CMAKE_CXX_COMPILER_ID MATCHES "MSVC")
    if (CMAKE_BUILD_TYPE MATCHES "Debug" AND MSVC_RUNTIME_TYPE)
        set (MSVC_RUNTIME_TYPE "${MSVC_RUNTIME_TYPE}d")
    endif ()

    set (CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} ${MSVC_RUNTIME_TYPE}")
    set (CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} ${MSVC_RUNTIME_TYPE}")
    set (CMAKE_CXX_FLAGS_RELWITHDEBINFO "${CMAKE_CXX_FLAGS_RELWITHDEBINFO} ${MSVC_RUNTIME_TYPE}")
    set (CMAKE_EXE_LINKER_FLAGS_RELWITHDEBINFO "/PROFILE")

    message (STATUS "Build type: ${CMAKE_BUILD_TYPE}")
    message (STATUS "USE MSVC RUNTIME: ${MSVC_RUNTIME_TYPE}")
endif()

find_package(Backward REQUIRED)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE Backward::Backward)
