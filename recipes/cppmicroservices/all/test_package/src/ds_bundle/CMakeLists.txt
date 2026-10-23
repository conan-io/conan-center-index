find_program(US_SCRCODEGEN_EXECUTABLE
  NAMES SCRCodeGen3 SCRCodeGen
  REQUIRED
)

set(_glue_file ${CMAKE_CURRENT_BINARY_DIR}/autogen_test_greeter_ds_Glue.cpp)

add_custom_command(
  OUTPUT ${_glue_file}
  COMMAND ${US_SCRCODEGEN_EXECUTABLE}
    --manifest ${CMAKE_CURRENT_SOURCE_DIR}/manifest.json
    --out-file ${_glue_file}
    --include-headers GreeterDSImpl.hpp
  DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/manifest.json
  COMMENT "Generating DS glue code for test_greeter_ds"
  VERBATIM
)

set(_bundle_srcs
  ${CMAKE_CURRENT_SOURCE_DIR}/GreeterDSImpl.cpp
  ${_glue_file}
)

usFunctionGetResourceSource(TARGET test_greeter_ds OUT _bundle_srcs)
usFunctionGenerateBundleInit(TARGET test_greeter_ds OUT _bundle_srcs)

add_library(test_greeter_ds SHARED ${_bundle_srcs})
target_include_directories(test_greeter_ds PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}
)
target_link_libraries(test_greeter_ds PRIVATE
  CppMicroServices
  usServiceComponent
  TestGreeterInterface
)
set_target_properties(test_greeter_ds PROPERTIES
  COMPILE_DEFINITIONS US_BUNDLE_NAME=test_greeter_ds
  US_BUNDLE_NAME test_greeter_ds
  CXX_VISIBILITY_PRESET hidden
  VISIBILITY_INLINES_HIDDEN 1
)
usFunctionEmbedResources(TARGET test_greeter_ds
  WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
  FILES manifest.json
)
