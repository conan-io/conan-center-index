########### AGGREGATED COMPONENTS AND DEPENDENCIES FOR THE MULTI CONFIG #####################
#############################################################################################

set(aws-c-compression_COMPONENT_NAMES "")
if(DEFINED aws-c-compression_FIND_DEPENDENCY_NAMES)
  list(APPEND aws-c-compression_FIND_DEPENDENCY_NAMES aws-c-common)
  list(REMOVE_DUPLICATES aws-c-compression_FIND_DEPENDENCY_NAMES)
else()
  set(aws-c-compression_FIND_DEPENDENCY_NAMES aws-c-common)
endif()
set(aws-c-common_FIND_MODE "NO_MODULE")

########### VARIABLES #######################################################################
#############################################################################################
set(aws-c-compression_PACKAGE_FOLDER_DEBUG "C:/Users/MH.Rezaiy_110/.conan2/p/b/aws-c3735d11a8f1fa/p")
set(aws-c-compression_BUILD_MODULES_PATHS_DEBUG )


set(aws-c-compression_INCLUDE_DIRS_DEBUG "${aws-c-compression_PACKAGE_FOLDER_DEBUG}/include")
set(aws-c-compression_RES_DIRS_DEBUG )
set(aws-c-compression_DEFINITIONS_DEBUG )
set(aws-c-compression_SHARED_LINK_FLAGS_DEBUG )
set(aws-c-compression_EXE_LINK_FLAGS_DEBUG )
set(aws-c-compression_OBJECTS_DEBUG )
set(aws-c-compression_COMPILE_DEFINITIONS_DEBUG )
set(aws-c-compression_COMPILE_OPTIONS_C_DEBUG )
set(aws-c-compression_COMPILE_OPTIONS_CXX_DEBUG )
set(aws-c-compression_LIB_DIRS_DEBUG "${aws-c-compression_PACKAGE_FOLDER_DEBUG}/lib")
set(aws-c-compression_BIN_DIRS_DEBUG )
set(aws-c-compression_LIBRARY_TYPE_DEBUG STATIC)
set(aws-c-compression_IS_HOST_WINDOWS_DEBUG 1)
set(aws-c-compression_LIBS_DEBUG aws-c-compression)
set(aws-c-compression_SYSTEM_LIBS_DEBUG )
set(aws-c-compression_FRAMEWORK_DIRS_DEBUG )
set(aws-c-compression_FRAMEWORKS_DEBUG )
set(aws-c-compression_BUILD_DIRS_DEBUG )
set(aws-c-compression_NO_SONAME_MODE_DEBUG FALSE)


# COMPOUND VARIABLES
set(aws-c-compression_COMPILE_OPTIONS_DEBUG
    "$<$<COMPILE_LANGUAGE:CXX>:${aws-c-compression_COMPILE_OPTIONS_CXX_DEBUG}>"
    "$<$<COMPILE_LANGUAGE:C>:${aws-c-compression_COMPILE_OPTIONS_C_DEBUG}>")
set(aws-c-compression_LINKER_FLAGS_DEBUG
    "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:${aws-c-compression_SHARED_LINK_FLAGS_DEBUG}>"
    "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:${aws-c-compression_SHARED_LINK_FLAGS_DEBUG}>"
    "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:${aws-c-compression_EXE_LINK_FLAGS_DEBUG}>")


set(aws-c-compression_COMPONENTS_DEBUG )