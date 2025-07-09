project(test_bundle)

set(_glue_file ${CMAKE_CURRENT_BINARY_DIR}/autogen_test_bundle_Glue.cpp)
set(_srcs src/TestBundleImpl.cpp ${_glue_file})
usFunctionGetResourceSource(TARGET test_bundle OUT _srcs)
usFunctionGenerateBundleInit(TARGET test_bundle OUT _srcs)

message(STATUS "===================================== CMAKE_CURRENT_BINARY_DIR=${CMAKE_CURRENT_BINARY_DIR}")

add_library(test_bundle ${_srcs})
set_property(TARGET test_bundle APPEND PROPERTY COMPILE_DEFINITIONS US_BUNDLE_NAME=test_bundle)
set_property(TARGET test_bundle PROPERTY DEBUG_POSTFIX "")
target_link_libraries(test_bundle ${CppMicroServices_LIBRARIES} ${US_ServiceComponent_LIBRARIES})
target_include_directories(test_bundle PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/src)

# Add in rule for how to build the autogen source for the glue
add_custom_command(
    OUTPUT ${_glue_file}
    COMMAND $<TARGET_FILE:SCRCodeGen> --manifest ${CMAKE_CURRENT_SOURCE_DIR}/manifest.json --out-file ${_glue_file} --include-headers ServiceComponents.hpp
    DEPENDS SCRCodeGen usServiceComponent ${CMAKE_CURRENT_SOURCE_DIR}/manifest.json
    COMMENT "Generate bundle activator based on manifest.json"
    VERBATIM)
  
usFunctionAddResources(TARGET test_bundle BUNDLE_NAME test_bundle WORKING_DIRECTORY ${PROJECT_SOURCE_DIR} FILES manifest.json)
usFunctionEmbedResources(TARGET test_bundle)
