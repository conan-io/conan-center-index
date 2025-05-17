########### AGGREGATED COMPONENTS AND DEPENDENCIES FOR THE MULTI CONFIG #####################
#############################################################################################

set(aws-c-auth_COMPONENT_NAMES "")
if(DEFINED aws-c-auth_FIND_DEPENDENCY_NAMES)
  list(APPEND aws-c-auth_FIND_DEPENDENCY_NAMES aws-c-http aws-c-io aws-c-cal aws-c-sdkutils aws-c-common)
  list(REMOVE_DUPLICATES aws-c-auth_FIND_DEPENDENCY_NAMES)
else()
  set(aws-c-auth_FIND_DEPENDENCY_NAMES aws-c-http aws-c-io aws-c-cal aws-c-sdkutils aws-c-common)
endif()
set(aws-c-http_FIND_MODE "NO_MODULE")
set(aws-c-io_FIND_MODE "NO_MODULE")
set(aws-c-cal_FIND_MODE "NO_MODULE")
set(aws-c-sdkutils_FIND_MODE "NO_MODULE")
set(aws-c-common_FIND_MODE "NO_MODULE")

########### VARIABLES #######################################################################
#############################################################################################
set(aws-c-auth_PACKAGE_FOLDER_DEBUG "C:/Users/MH.Rezaiy_110/.conan2/p/b/aws-c26d02442b00a4/p")
set(aws-c-auth_BUILD_MODULES_PATHS_DEBUG )


set(aws-c-auth_INCLUDE_DIRS_DEBUG "${aws-c-auth_PACKAGE_FOLDER_DEBUG}/include")
set(aws-c-auth_RES_DIRS_DEBUG )
set(aws-c-auth_DEFINITIONS_DEBUG )
set(aws-c-auth_SHARED_LINK_FLAGS_DEBUG )
set(aws-c-auth_EXE_LINK_FLAGS_DEBUG )
set(aws-c-auth_OBJECTS_DEBUG )
set(aws-c-auth_COMPILE_DEFINITIONS_DEBUG )
set(aws-c-auth_COMPILE_OPTIONS_C_DEBUG )
set(aws-c-auth_COMPILE_OPTIONS_CXX_DEBUG )
set(aws-c-auth_LIB_DIRS_DEBUG "${aws-c-auth_PACKAGE_FOLDER_DEBUG}/lib")
set(aws-c-auth_BIN_DIRS_DEBUG )
set(aws-c-auth_LIBRARY_TYPE_DEBUG STATIC)
set(aws-c-auth_IS_HOST_WINDOWS_DEBUG 1)
set(aws-c-auth_LIBS_DEBUG aws-c-auth)
set(aws-c-auth_SYSTEM_LIBS_DEBUG )
set(aws-c-auth_FRAMEWORK_DIRS_DEBUG )
set(aws-c-auth_FRAMEWORKS_DEBUG )
set(aws-c-auth_BUILD_DIRS_DEBUG )
set(aws-c-auth_NO_SONAME_MODE_DEBUG FALSE)


# COMPOUND VARIABLES
set(aws-c-auth_COMPILE_OPTIONS_DEBUG
    "$<$<COMPILE_LANGUAGE:CXX>:${aws-c-auth_COMPILE_OPTIONS_CXX_DEBUG}>"
    "$<$<COMPILE_LANGUAGE:C>:${aws-c-auth_COMPILE_OPTIONS_C_DEBUG}>")
set(aws-c-auth_LINKER_FLAGS_DEBUG
    "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:${aws-c-auth_SHARED_LINK_FLAGS_DEBUG}>"
    "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:${aws-c-auth_SHARED_LINK_FLAGS_DEBUG}>"
    "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:${aws-c-auth_EXE_LINK_FLAGS_DEBUG}>")


set(aws-c-auth_COMPONENTS_DEBUG )