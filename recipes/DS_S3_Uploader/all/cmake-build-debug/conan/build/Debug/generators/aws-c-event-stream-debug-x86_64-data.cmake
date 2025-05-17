########### AGGREGATED COMPONENTS AND DEPENDENCIES FOR THE MULTI CONFIG #####################
#############################################################################################

set(aws-c-event-stream_COMPONENT_NAMES "")
if(DEFINED aws-c-event-stream_FIND_DEPENDENCY_NAMES)
  list(APPEND aws-c-event-stream_FIND_DEPENDENCY_NAMES aws-c-io aws-checksums aws-c-common)
  list(REMOVE_DUPLICATES aws-c-event-stream_FIND_DEPENDENCY_NAMES)
else()
  set(aws-c-event-stream_FIND_DEPENDENCY_NAMES aws-c-io aws-checksums aws-c-common)
endif()
set(aws-c-io_FIND_MODE "NO_MODULE")
set(aws-checksums_FIND_MODE "NO_MODULE")
set(aws-c-common_FIND_MODE "NO_MODULE")

########### VARIABLES #######################################################################
#############################################################################################
set(aws-c-event-stream_PACKAGE_FOLDER_DEBUG "C:/Users/MH.Rezaiy_110/.conan2/p/b/aws-c5d987d5a7bcf5/p")
set(aws-c-event-stream_BUILD_MODULES_PATHS_DEBUG )


set(aws-c-event-stream_INCLUDE_DIRS_DEBUG "${aws-c-event-stream_PACKAGE_FOLDER_DEBUG}/include")
set(aws-c-event-stream_RES_DIRS_DEBUG )
set(aws-c-event-stream_DEFINITIONS_DEBUG )
set(aws-c-event-stream_SHARED_LINK_FLAGS_DEBUG )
set(aws-c-event-stream_EXE_LINK_FLAGS_DEBUG )
set(aws-c-event-stream_OBJECTS_DEBUG )
set(aws-c-event-stream_COMPILE_DEFINITIONS_DEBUG )
set(aws-c-event-stream_COMPILE_OPTIONS_C_DEBUG )
set(aws-c-event-stream_COMPILE_OPTIONS_CXX_DEBUG )
set(aws-c-event-stream_LIB_DIRS_DEBUG "${aws-c-event-stream_PACKAGE_FOLDER_DEBUG}/lib")
set(aws-c-event-stream_BIN_DIRS_DEBUG )
set(aws-c-event-stream_LIBRARY_TYPE_DEBUG STATIC)
set(aws-c-event-stream_IS_HOST_WINDOWS_DEBUG 1)
set(aws-c-event-stream_LIBS_DEBUG aws-c-event-stream)
set(aws-c-event-stream_SYSTEM_LIBS_DEBUG )
set(aws-c-event-stream_FRAMEWORK_DIRS_DEBUG )
set(aws-c-event-stream_FRAMEWORKS_DEBUG )
set(aws-c-event-stream_BUILD_DIRS_DEBUG )
set(aws-c-event-stream_NO_SONAME_MODE_DEBUG FALSE)


# COMPOUND VARIABLES
set(aws-c-event-stream_COMPILE_OPTIONS_DEBUG
    "$<$<COMPILE_LANGUAGE:CXX>:${aws-c-event-stream_COMPILE_OPTIONS_CXX_DEBUG}>"
    "$<$<COMPILE_LANGUAGE:C>:${aws-c-event-stream_COMPILE_OPTIONS_C_DEBUG}>")
set(aws-c-event-stream_LINKER_FLAGS_DEBUG
    "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:${aws-c-event-stream_SHARED_LINK_FLAGS_DEBUG}>"
    "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:${aws-c-event-stream_SHARED_LINK_FLAGS_DEBUG}>"
    "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:${aws-c-event-stream_EXE_LINK_FLAGS_DEBUG}>")


set(aws-c-event-stream_COMPONENTS_DEBUG )