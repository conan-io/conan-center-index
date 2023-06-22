cmake_minimum_required(VERSION 3.8)
project(test_package CXX)

# Set compiler flags for x86_64 architecture
if(CMAKE_SYSTEM_PROCESSOR STREQUAL "x86_64")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -march=haswell")
endif()

# Set compiler flags for armv7 architecture
if(CMAKE_SYSTEM_PROCESSOR STREQUAL "armv7")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -march=armv7")
endif()

# Set compiler flags for armv8 architecture
if(CMAKE_SYSTEM_PROCESSOR STREQUAL "armv8")
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -march=armv8-a")
endif()

find_package(Platform.Ranges REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE Platform.Ranges::Platform.Ranges)
set_target_properties(${PROJECT_NAME} PROPERTIES CXX_STANDARD 20)