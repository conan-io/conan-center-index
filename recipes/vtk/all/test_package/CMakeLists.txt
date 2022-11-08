cmake_minimum_required(VERSION 3.8)

project(test_package CXX)

find_package (VTK COMPONENTS CommonCore REQUIRED CONFIG)

if (NOT DEFINED VTK_ENABLE_KITS)
   message(FATAL_ERROR "Expected VTK_ENABLE_KITS to be defined via conan-official-vtk-variables.cmake")
endif ()

add_executable(${PROJECT_NAME} test_package.cpp)

if (VTK_ENABLE_KITS)
   target_link_libraries(${PROJECT_NAME} VTK::Common)
else ()
   target_link_libraries(${PROJECT_NAME} VTK::CommonCore)
endif ()
