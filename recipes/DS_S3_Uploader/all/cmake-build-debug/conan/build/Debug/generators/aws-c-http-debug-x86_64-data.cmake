########### AGGREGATED COMPONENTS AND DEPENDENCIES FOR THE MULTI CONFIG #####################
#############################################################################################

set(aws-c-http_COMPONENT_NAMES "")
if(DEFINED aws-c-http_FIND_DEPENDENCY_NAMES)
  list(APPEND aws-c-http_FIND_DEPENDENCY_NAMES aws-c-compression aws-c-io aws-c-cal aws-c-common)
  list(REMOVE_DUPLICATES aws-c-http_FIND_DEPENDENCY_NAMES)
else()
  set(aws-c-http_FIND_DEPENDENCY_NAMES aws-c-compression aws-c-io aws-c-cal aws-c-common)
endif()
set(aws-c-compression_FIND_MODE "NO_MODULE")
set(aws-c-io_FIND_MODE "NO_MODULE")
set(aws-c-cal_FIND_MODE "NO_MODULE")
set(aws-c-common_FIND_MODE "NO_MODULE")

########### VARIABLES #######################################################################
#############################################################################################
set(aws-c-http_PACKAGE_FOLDER_DEBUG "C:/Users/MH.Rezaiy_110/.conan2/p/b/aws-c8491e9ae7717b/p")
set(aws-c-http_BUILD_MODULES_PATHS_DEBUG )


set(aws-c-http_INCLUDE_DIRS_DEBUG "${aws-c-http_PACKAGE_FOLDER_DEBUG}/include")
set(aws-c-http_RES_DIRS_DEBUG )
set(aws-c-http_DEFINITIONS_DEBUG )
set(aws-c-http_SHARED_LINK_FLAGS_DEBUG )
set(aws-c-http_EXE_LINK_FLAGS_DEBUG )
set(aws-c-http_OBJECTS_DEBUG )
set(aws-c-http_COMPILE_DEFINITIONS_DEBUG )
set(aws-c-http_COMPILE_OPTIONS_C_DEBUG )
set(aws-c-http_COMPILE_OPTIONS_CXX_DEBUG )
set(aws-c-http_LIB_DIRS_DEBUG "${aws-c-http_PACKAGE_FOLDER_DEBUG}/lib")
set(aws-c-http_BIN_DIRS_DEBUG )
set(aws-c-http_LIBRARY_TYPE_DEBUG STATIC)
set(aws-c-http_IS_HOST_WINDOWS_DEBUG 1)
set(aws-c-http_LIBS_DEBUG aws-c-http)
set(aws-c-http_SYSTEM_LIBS_DEBUG )
set(aws-c-http_FRAMEWORK_DIRS_DEBUG )
set(aws-c-http_FRAMEWORKS_DEBUG )
set(aws-c-http_BUILD_DIRS_DEBUG )
set(aws-c-http_NO_SONAME_MODE_DEBUG FALSE)


# COMPOUND VARIABLES
set(aws-c-http_COMPILE_OPTIONS_DEBUG
    "$<$<COMPILE_LANGUAGE:CXX>:${aws-c-http_COMPILE_OPTIONS_CXX_DEBUG}>"
    "$<$<COMPILE_LANGUAGE:C>:${aws-c-http_COMPILE_OPTIONS_C_DEBUG}>")
set(aws-c-http_LINKER_FLAGS_DEBUG
    "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:${aws-c-http_SHARED_LINK_FLAGS_DEBUG}>"
    "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:${aws-c-http_SHARED_LINK_FLAGS_DEBUG}>"
    "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:${aws-c-http_EXE_LINK_FLAGS_DEBUG}>")


set(aws-c-http_COMPONENTS_DEBUG )