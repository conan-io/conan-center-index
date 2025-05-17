########### AGGREGATED COMPONENTS AND DEPENDENCIES FOR THE MULTI CONFIG #####################
#############################################################################################

set(aws-c-io_COMPONENT_NAMES "")
if(DEFINED aws-c-io_FIND_DEPENDENCY_NAMES)
  list(APPEND aws-c-io_FIND_DEPENDENCY_NAMES aws-c-cal aws-c-common)
  list(REMOVE_DUPLICATES aws-c-io_FIND_DEPENDENCY_NAMES)
else()
  set(aws-c-io_FIND_DEPENDENCY_NAMES aws-c-cal aws-c-common)
endif()
set(aws-c-cal_FIND_MODE "NO_MODULE")
set(aws-c-common_FIND_MODE "NO_MODULE")

########### VARIABLES #######################################################################
#############################################################################################
set(aws-c-io_PACKAGE_FOLDER_DEBUG "C:/Users/MH.Rezaiy_110/.conan2/p/b/aws-cbfa156d0c4c20/p")
set(aws-c-io_BUILD_MODULES_PATHS_DEBUG )


set(aws-c-io_INCLUDE_DIRS_DEBUG "${aws-c-io_PACKAGE_FOLDER_DEBUG}/include")
set(aws-c-io_RES_DIRS_DEBUG )
set(aws-c-io_DEFINITIONS_DEBUG )
set(aws-c-io_SHARED_LINK_FLAGS_DEBUG )
set(aws-c-io_EXE_LINK_FLAGS_DEBUG )
set(aws-c-io_OBJECTS_DEBUG )
set(aws-c-io_COMPILE_DEFINITIONS_DEBUG )
set(aws-c-io_COMPILE_OPTIONS_C_DEBUG )
set(aws-c-io_COMPILE_OPTIONS_CXX_DEBUG )
set(aws-c-io_LIB_DIRS_DEBUG "${aws-c-io_PACKAGE_FOLDER_DEBUG}/lib")
set(aws-c-io_BIN_DIRS_DEBUG )
set(aws-c-io_LIBRARY_TYPE_DEBUG STATIC)
set(aws-c-io_IS_HOST_WINDOWS_DEBUG 1)
set(aws-c-io_LIBS_DEBUG aws-c-io)
set(aws-c-io_SYSTEM_LIBS_DEBUG crypt32 secur32 shlwapi)
set(aws-c-io_FRAMEWORK_DIRS_DEBUG )
set(aws-c-io_FRAMEWORKS_DEBUG )
set(aws-c-io_BUILD_DIRS_DEBUG )
set(aws-c-io_NO_SONAME_MODE_DEBUG FALSE)


# COMPOUND VARIABLES
set(aws-c-io_COMPILE_OPTIONS_DEBUG
    "$<$<COMPILE_LANGUAGE:CXX>:${aws-c-io_COMPILE_OPTIONS_CXX_DEBUG}>"
    "$<$<COMPILE_LANGUAGE:C>:${aws-c-io_COMPILE_OPTIONS_C_DEBUG}>")
set(aws-c-io_LINKER_FLAGS_DEBUG
    "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:${aws-c-io_SHARED_LINK_FLAGS_DEBUG}>"
    "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:${aws-c-io_SHARED_LINK_FLAGS_DEBUG}>"
    "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:${aws-c-io_EXE_LINK_FLAGS_DEBUG}>")


set(aws-c-io_COMPONENTS_DEBUG )