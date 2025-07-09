#=========================================================
# The executable managing the CppMicroServices framework
#---------------------------------------------------------

set(_srcs src/main.cpp)

get_target_property(DS_DLL_PATH DeclarativeServices IMPORTED_LOCATION_RELEASE)
message(STATUS "==================================================== DS_DLL_Path = ${DS_DLL_PATH}")
set_source_files_properties(
  src/main.cpp
  PROPERTIES
  COMPILE_FLAGS "-DDS_DLL_PATH=\"${DS_DLL_PATH}\"")

if(NOT BUILD_SHARED_LIBS)
  # Set up dependencies to resources from static bundles
  usFunctionGetResourceSource(TARGET test_app OUT _srcs)
endif()

add_executable(test_app)
target_sources(test_app PRIVATE ${_srcs})

if(NOT BUILD_SHARED_LIBS)
  target_link_libraries(test_app ${_static_bundles})
  usFunctionEmbedResources(TARGET test_app
    # The executable is not a bundle itself but we still
    # need a bundle name for it here.
    BUNDLE_NAME test_app
    # Merge in all resources from static bundles
    ZIP_ARCHIVES ${_static_bundles}
    )
else()
  target_link_libraries(test_app ${CppMicroServices_LIBRARIES})
endif()

if(WIN32)
  add_custom_command(TARGET test_app POST_BUILD
  COMMAND ${CMAKE_COMMAND} -E copy_if_different
          $<TARGET_RUNTIME_DLLS:test_app>
          $<TARGET_FILE_DIR:test_app>
  COMMAND_EXPAND_LISTS
  )
endif()

install(TARGETS test_app)
