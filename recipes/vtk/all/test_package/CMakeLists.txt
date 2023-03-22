cmake_minimum_required(VERSION 3.8)

project(test_package CXX)

# Note: testing with RenderingFreeType to check autoinit is working
# TODO make test different depending on what modules were enabled. ie don't test with this if not built!
find_package (VTK COMPONENTS CommonCore RenderingFreeType REQUIRED CONFIG)

if (NOT DEFINED VTK_ENABLE_KITS)
   message(FATAL_ERROR "Expected VTK_ENABLE_KITS to be defined via conan-official-vtk-variables.cmake")
endif ()

add_executable(${PROJECT_NAME} test_package.cpp)

# Again: may not want to link to diff things
# ALSO note: even with Kits enabled, we should be able to use the module-names for linking.
if (VTK_ENABLE_KITS)
   target_link_libraries(${PROJECT_NAME} VTK::Common VTK::Rendering)
else ()
   target_link_libraries(${PROJECT_NAME} VTK::CommonCore VTK::RenderingFreeType)
endif ()
