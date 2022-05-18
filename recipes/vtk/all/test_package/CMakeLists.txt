cmake_minimum_required(VERSION 3.16)
project(test_package)

find_package (VTK
   COMPONENTS
      CommonCore
   REQUIRED
   )

if (NOT DEFINED VTK_ENABLE_KITS)
   message(FATAL_ERROR "Expected VTK_ENABLE_KITS to be defined via conan-official-vtk-variables.cmake")
endif ()

file(GLOB SOURCE_FILES *.cpp)

add_executable(${PROJECT_NAME} ${SOURCE_FILES})

if (VTK_ENABLE_KITS)
   target_link_libraries(${PROJECT_NAME}
      VTK::Common
   )
else ()
   target_link_libraries(${PROJECT_NAME}
      VTK::CommonCore
   )
endif ()

target_link_libraries(${PROJECT_NAME}
   VTK::loguru
   VTK::sys
   )
