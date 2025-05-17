########### AGGREGATED COMPONENTS AND DEPENDENCIES FOR THE MULTI CONFIG #####################
#############################################################################################

set(aws-c-mqtt_COMPONENT_NAMES "")
if(DEFINED aws-c-mqtt_FIND_DEPENDENCY_NAMES)
  list(APPEND aws-c-mqtt_FIND_DEPENDENCY_NAMES aws-c-http aws-c-io aws-c-cal aws-c-common)
  list(REMOVE_DUPLICATES aws-c-mqtt_FIND_DEPENDENCY_NAMES)
else()
  set(aws-c-mqtt_FIND_DEPENDENCY_NAMES aws-c-http aws-c-io aws-c-cal aws-c-common)
endif()
set(aws-c-http_FIND_MODE "NO_MODULE")
set(aws-c-io_FIND_MODE "NO_MODULE")
set(aws-c-cal_FIND_MODE "NO_MODULE")
set(aws-c-common_FIND_MODE "NO_MODULE")

########### VARIABLES #######################################################################
#############################################################################################
set(aws-c-mqtt_PACKAGE_FOLDER_DEBUG "C:/Users/MH.Rezaiy_110/.conan2/p/b/aws-c98ee5e3e8e81a/p")
set(aws-c-mqtt_BUILD_MODULES_PATHS_DEBUG )


set(aws-c-mqtt_INCLUDE_DIRS_DEBUG "${aws-c-mqtt_PACKAGE_FOLDER_DEBUG}/include")
set(aws-c-mqtt_RES_DIRS_DEBUG )
set(aws-c-mqtt_DEFINITIONS_DEBUG )
set(aws-c-mqtt_SHARED_LINK_FLAGS_DEBUG )
set(aws-c-mqtt_EXE_LINK_FLAGS_DEBUG )
set(aws-c-mqtt_OBJECTS_DEBUG )
set(aws-c-mqtt_COMPILE_DEFINITIONS_DEBUG )
set(aws-c-mqtt_COMPILE_OPTIONS_C_DEBUG )
set(aws-c-mqtt_COMPILE_OPTIONS_CXX_DEBUG )
set(aws-c-mqtt_LIB_DIRS_DEBUG "${aws-c-mqtt_PACKAGE_FOLDER_DEBUG}/lib")
set(aws-c-mqtt_BIN_DIRS_DEBUG )
set(aws-c-mqtt_LIBRARY_TYPE_DEBUG STATIC)
set(aws-c-mqtt_IS_HOST_WINDOWS_DEBUG 1)
set(aws-c-mqtt_LIBS_DEBUG aws-c-mqtt)
set(aws-c-mqtt_SYSTEM_LIBS_DEBUG )
set(aws-c-mqtt_FRAMEWORK_DIRS_DEBUG )
set(aws-c-mqtt_FRAMEWORKS_DEBUG )
set(aws-c-mqtt_BUILD_DIRS_DEBUG )
set(aws-c-mqtt_NO_SONAME_MODE_DEBUG FALSE)


# COMPOUND VARIABLES
set(aws-c-mqtt_COMPILE_OPTIONS_DEBUG
    "$<$<COMPILE_LANGUAGE:CXX>:${aws-c-mqtt_COMPILE_OPTIONS_CXX_DEBUG}>"
    "$<$<COMPILE_LANGUAGE:C>:${aws-c-mqtt_COMPILE_OPTIONS_C_DEBUG}>")
set(aws-c-mqtt_LINKER_FLAGS_DEBUG
    "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:${aws-c-mqtt_SHARED_LINK_FLAGS_DEBUG}>"
    "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:${aws-c-mqtt_SHARED_LINK_FLAGS_DEBUG}>"
    "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:${aws-c-mqtt_EXE_LINK_FLAGS_DEBUG}>")


set(aws-c-mqtt_COMPONENTS_DEBUG )