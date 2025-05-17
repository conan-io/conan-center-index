########### AGGREGATED COMPONENTS AND DEPENDENCIES FOR THE MULTI CONFIG #####################
#############################################################################################

set(aws-c-s3_COMPONENT_NAMES "")
if(DEFINED aws-c-s3_FIND_DEPENDENCY_NAMES)
  list(APPEND aws-c-s3_FIND_DEPENDENCY_NAMES aws-c-auth aws-c-http aws-c-io aws-c-cal aws-checksums aws-c-common)
  list(REMOVE_DUPLICATES aws-c-s3_FIND_DEPENDENCY_NAMES)
else()
  set(aws-c-s3_FIND_DEPENDENCY_NAMES aws-c-auth aws-c-http aws-c-io aws-c-cal aws-checksums aws-c-common)
endif()
set(aws-c-auth_FIND_MODE "NO_MODULE")
set(aws-c-http_FIND_MODE "NO_MODULE")
set(aws-c-io_FIND_MODE "NO_MODULE")
set(aws-c-cal_FIND_MODE "NO_MODULE")
set(aws-checksums_FIND_MODE "NO_MODULE")
set(aws-c-common_FIND_MODE "NO_MODULE")

########### VARIABLES #######################################################################
#############################################################################################
set(aws-c-s3_PACKAGE_FOLDER_DEBUG "C:/Users/MH.Rezaiy_110/.conan2/p/b/aws-c4de602caf9f8b/p")
set(aws-c-s3_BUILD_MODULES_PATHS_DEBUG )


set(aws-c-s3_INCLUDE_DIRS_DEBUG )
set(aws-c-s3_RES_DIRS_DEBUG )
set(aws-c-s3_DEFINITIONS_DEBUG )
set(aws-c-s3_SHARED_LINK_FLAGS_DEBUG )
set(aws-c-s3_EXE_LINK_FLAGS_DEBUG )
set(aws-c-s3_OBJECTS_DEBUG )
set(aws-c-s3_COMPILE_DEFINITIONS_DEBUG )
set(aws-c-s3_COMPILE_OPTIONS_C_DEBUG )
set(aws-c-s3_COMPILE_OPTIONS_CXX_DEBUG )
set(aws-c-s3_LIB_DIRS_DEBUG "${aws-c-s3_PACKAGE_FOLDER_DEBUG}/lib")
set(aws-c-s3_BIN_DIRS_DEBUG )
set(aws-c-s3_LIBRARY_TYPE_DEBUG STATIC)
set(aws-c-s3_IS_HOST_WINDOWS_DEBUG 1)
set(aws-c-s3_LIBS_DEBUG aws-c-s3)
set(aws-c-s3_SYSTEM_LIBS_DEBUG )
set(aws-c-s3_FRAMEWORK_DIRS_DEBUG )
set(aws-c-s3_FRAMEWORKS_DEBUG )
set(aws-c-s3_BUILD_DIRS_DEBUG )
set(aws-c-s3_NO_SONAME_MODE_DEBUG FALSE)


# COMPOUND VARIABLES
set(aws-c-s3_COMPILE_OPTIONS_DEBUG
    "$<$<COMPILE_LANGUAGE:CXX>:${aws-c-s3_COMPILE_OPTIONS_CXX_DEBUG}>"
    "$<$<COMPILE_LANGUAGE:C>:${aws-c-s3_COMPILE_OPTIONS_C_DEBUG}>")
set(aws-c-s3_LINKER_FLAGS_DEBUG
    "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:${aws-c-s3_SHARED_LINK_FLAGS_DEBUG}>"
    "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:${aws-c-s3_SHARED_LINK_FLAGS_DEBUG}>"
    "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:${aws-c-s3_EXE_LINK_FLAGS_DEBUG}>")


set(aws-c-s3_COMPONENTS_DEBUG )