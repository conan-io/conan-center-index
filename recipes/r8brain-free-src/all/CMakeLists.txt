cmake_minimum_required(VERSION 3.1)
project(r8brain-free-src CXX)

include(conanbuildinfo.cmake)
conan_basic_setup()

add_library(r8brain source_subfolder/r8bbase.cpp)
if(MSVC AND BUILD_SHARED_LIBS)
  set_property(TARGET r8brain PROPERTY WINDOWS_EXPORT_ALL_SYMBOLS TRUE)
endif()

install(
  TARGETS r8brain
  RUNTIME DESTINATION bin
  LIBRARY DESTINATION lib
  ARCHIVE DESTINATION lib
)

file(GLOB PUBLIC_HEADERS ${CMAKE_CURRENT_SOURCE_DIR}/source_subfolder/*.h)
install(FILES ${PUBLIC_HEADERS} DESTINATION include)
