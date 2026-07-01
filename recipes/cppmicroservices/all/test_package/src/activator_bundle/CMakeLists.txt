set(_bundle_srcs
  ${CMAKE_CURRENT_SOURCE_DIR}/GreeterActivatorImpl.cpp
)

usFunctionGetResourceSource(TARGET test_greeter_activator OUT _bundle_srcs)
usFunctionGenerateBundleInit(TARGET test_greeter_activator OUT _bundle_srcs)

add_library(test_greeter_activator SHARED ${_bundle_srcs})
target_include_directories(test_greeter_activator PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}
)
target_link_libraries(test_greeter_activator PRIVATE
  CppMicroServices
  TestGreeterInterface
)
set_target_properties(test_greeter_activator PROPERTIES
  COMPILE_DEFINITIONS US_BUNDLE_NAME=test_greeter_activator
  US_BUNDLE_NAME test_greeter_activator
  CXX_VISIBILITY_PRESET hidden
  VISIBILITY_INLINES_HIDDEN 1
)
usFunctionEmbedResources(TARGET test_greeter_activator
  WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
  FILES manifest.json
)
