cmake_minimum_required(VERSION 3.17)
project(CppMicroServicesTestPackage CXX)

find_package(CppMicroServices REQUIRED)

include(GenerateExportHeader)

# Place all build artifacts in the same directory so bundles are easy to find at runtime.
# Using a single directory avoids platform differences (DLLs go to RUNTIME on Windows,
# shared libs go to LIBRARY on Unix).
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
# Prevent multi-config generators from appending a per-config subdirectory.
foreach(config IN ITEMS DEBUG RELEASE RELWITHDEBINFO MINSIZEREL)
  set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_${config} ${CMAKE_BINARY_DIR}/bin)
  set(CMAKE_LIBRARY_OUTPUT_DIRECTORY_${config} ${CMAKE_BINARY_DIR}/bin)
endforeach()

# --- Shared interface library ---
add_library(TestGreeterInterface SHARED
  src/IGreeter.cpp
  src/IGreeter.h
)
target_include_directories(TestGreeterInterface PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/src>
  $<BUILD_INTERFACE:${CMAKE_CURRENT_BINARY_DIR}>
)
generate_export_header(TestGreeterInterface
  EXPORT_FILE_NAME greeter_export.h
  EXPORT_MACRO_NAME GREETER_EXPORT
)
set_target_properties(TestGreeterInterface PROPERTIES
  CXX_VISIBILITY_PRESET hidden
  VISIBILITY_INLINES_HIDDEN 1
)

# --- Bundle ---
if(US_HAS_COMPENDIUM)
  add_subdirectory(src/ds_bundle)
else()
  add_subdirectory(src/activator_bundle)
endif()

# --- Test executable ---
add_executable(test_package src/main.cpp)
target_link_libraries(test_package PRIVATE
  CppMicroServices
  TestGreeterInterface
)

target_compile_definitions(test_package PRIVATE
  TEST_BUNDLE_DIR="${CMAKE_BINARY_DIR}/bin"
)

if(US_HAS_COMPENDIUM)
  target_link_libraries(test_package PRIVATE usServiceComponent)
  target_compile_definitions(test_package PRIVATE
    HAS_COMPENDIUM
    US_PACKAGE_BUNDLE_DIR="${US_PACKAGE_BUNDLE_DIR}"
  )
endif()
