cmake_minimum_required (VERSION 3.6)
project(test_package)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()
message(CONAN_LIBS: ${CONAN_LIBS})

  # Defines needed by Diligent
  add_definitions(-DDILIGENT_DEBUG)
  add_definitions(-DGL_SUPPORTED)
  add_definitions(-DVULKAN_SUPPORTED)
  if (WIN32)
    add_definitions(-DPLATFORM_WIN32)
  elseif(APPLE)
    add_definitions(-DPLATFORM_MACOS)
  elseif(UNIX)
    add_definitions(-DPLATFORM_LINUX)
  endif()
  # END Defines needed by Diligent

set(SOURCES test_package.cpp)

add_executable(${PROJECT_NAME} ${SOURCES})

target_link_libraries(${PROJECT_NAME} ${CONAN_LIBS})
