cmake_minimum_required(VERSION 3.15.0 FATAL_ERROR)
project(opene57_example CXX)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

option(BUILD_WITH_MT "Build with MultiThreaded Runtime" FALSE)

if(WIN32)
    set(MSVC_RUNTIME_TYPE $<IF:$<BOOL:${BUILD_WITH_MT}>,MultiThreaded$<$<CONFIG:Debug>:Debug>,MultiThreaded$<$<CONFIG:Debug>:Debug>>DLL)
endif()

find_package(opene57 REQUIRED CONFIG)

add_executable(${PROJECT_NAME} example.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE opene57::opene57)
set_target_properties(${PROJECT_NAME} PROPERTIES CXX_STANDARD 17)
