########### AGGREGATED COMPONENTS AND DEPENDENCIES FOR THE MULTI CONFIG #####################
#############################################################################################

set(aws-c-sdkutils_COMPONENT_NAMES "")
if(DEFINED aws-c-sdkutils_FIND_DEPENDENCY_NAMES)
  list(APPEND aws-c-sdkutils_FIND_DEPENDENCY_NAMES aws-c-common)
  list(REMOVE_DUPLICATES aws-c-sdkutils_FIND_DEPENDENCY_NAMES)
else()
  set(aws-c-sdkutils_FIND_DEPENDENCY_NAMES aws-c-common)
endif()
set(aws-c-common_FIND_MODE "NO_MODULE")

########### VARIABLES #######################################################################
#############################################################################################
set(aws-c-sdkutils_PACKAGE_FOLDER_DEBUG "C:/Users/MH.Rezaiy_110/.conan2/p/b/aws-c2cde206afa740/p")
set(aws-c-sdkutils_BUILD_MODULES_PATHS_DEBUG )


set(aws-c-sdkutils_INCLUDE_DIRS_DEBUG "${aws-c-sdkutils_PACKAGE_FOLDER_DEBUG}/include")
set(aws-c-sdkutils_RES_DIRS_DEBUG )
set(aws-c-sdkutils_DEFINITIONS_DEBUG )
set(aws-c-sdkutils_SHARED_LINK_FLAGS_DEBUG )
set(aws-c-sdkutils_EXE_LINK_FLAGS_DEBUG )
set(aws-c-sdkutils_OBJECTS_DEBUG )
set(aws-c-sdkutils_COMPILE_DEFINITIONS_DEBUG )
set(aws-c-sdkutils_COMPILE_OPTIONS_C_DEBUG )
set(aws-c-sdkutils_COMPILE_OPTIONS_CXX_DEBUG )
set(aws-c-sdkutils_LIB_DIRS_DEBUG "${aws-c-sdkutils_PACKAGE_FOLDER_DEBUG}/lib")
set(aws-c-sdkutils_BIN_DIRS_DEBUG )
set(aws-c-sdkutils_LIBRARY_TYPE_DEBUG STATIC)
set(aws-c-sdkutils_IS_HOST_WINDOWS_DEBUG 1)
set(aws-c-sdkutils_LIBS_DEBUG aws-c-sdkutils)
set(aws-c-sdkutils_SYSTEM_LIBS_DEBUG )
set(aws-c-sdkutils_FRAMEWORK_DIRS_DEBUG )
set(aws-c-sdkutils_FRAMEWORKS_DEBUG )
set(aws-c-sdkutils_BUILD_DIRS_DEBUG )
set(aws-c-sdkutils_NO_SONAME_MODE_DEBUG FALSE)


# COMPOUND VARIABLES
set(aws-c-sdkutils_COMPILE_OPTIONS_DEBUG
    "$<$<COMPILE_LANGUAGE:CXX>:${aws-c-sdkutils_COMPILE_OPTIONS_CXX_DEBUG}>"
    "$<$<COMPILE_LANGUAGE:C>:${aws-c-sdkutils_COMPILE_OPTIONS_C_DEBUG}>")
set(aws-c-sdkutils_LINKER_FLAGS_DEBUG
    "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,SHARED_LIBRARY>:${aws-c-sdkutils_SHARED_LINK_FLAGS_DEBUG}>"
    "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,MODULE_LIBRARY>:${aws-c-sdkutils_SHARED_LINK_FLAGS_DEBUG}>"
    "$<$<STREQUAL:$<TARGET_PROPERTY:TYPE>,EXECUTABLE>:${aws-c-sdkutils_EXE_LINK_FLAGS_DEBUG}>")


set(aws-c-sdkutils_COMPONENTS_DEBUG )