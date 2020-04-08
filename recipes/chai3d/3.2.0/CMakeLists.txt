cmake_minimum_required(VERSION 3.1.2)
project(cmake_wrapper)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup(TARGETS)

add_subdirectory("source_subfolder")

if (CHAI3D_WITH_GEL)
  add_subdirectory("source_subfolder/modules/GEL")
endif ()
if (CHAI3D_WITH_BULLET)
  add_subdirectory("source_subfolder/modules/BULLET")
endif ()
if (CHAI3D_WITH_ODE)
  add_subdirectory("source_subfolder/modules/ODE")
endif ()